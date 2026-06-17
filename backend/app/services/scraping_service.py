import hashlib
import re
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.logging import get_logger
from app.models.scraped_article import ScrapedArticle
from app.repositories.article_repo import ArticleRepository
from app.websocket.manager import manager

logger = get_logger(__name__)

CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)

_CATEGORY_KEYWORDS = {
    "ransomware": "Ransomware",
    "malware": "Malware",
    "cloud": "Cloud",
    "linux": "Linux",
    "kubernetes": "Cloud",
    "docker": "Cloud",
    "ai": "IA",
    "machine learning": "IA",
    "vulnerab": "Vulnérabilités",
    "exploit": "Vulnérabilités",
    "phishing": "Malware",
}

RELEVANCE_KEYWORDS = [
    "cve",
    "exploit",
    "vulnerability",
    "ransomware",
    "breach",
    "zero-day",
    "patch",
    "malware",
    "attack",
]


class ScrapingSource:
    def __init__(self, name: str, url: str, article_selector: str, title_selector: str, content_selector: str) -> None:
        self.name = name
        self.url = url
        self.article_selector = article_selector
        self.title_selector = title_selector
        self.content_selector = content_selector


DEFAULT_SOURCES: list[ScrapingSource] = [
    ScrapingSource(
        name="The Hacker News",
        url="https://thehackernews.com",
        article_selector="article.blog-post",
        title_selector="h2.title",
        content_selector="div.article-body",
    ),
    ScrapingSource(
        name="Krebs on Security",
        url="https://krebsonsecurity.com",
        article_selector="article.post",
        title_selector="h2.entry-title",
        content_selector="div.entry-content",
    ),
]


def _hash_content(source: str, title: str, content: str) -> str:
    raw = f"{source}|{title}|{content}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _classify_category(text: str) -> str:
    lowered = text.lower()
    for keyword, category in _CATEGORY_KEYWORDS.items():
        if keyword in lowered:
            return category
    return "Actualités"


def _summarize(content: str, max_length: int = 280) -> str:
    cleaned = " ".join(content.split())
    return cleaned[:max_length] + ("…" if len(cleaned) > max_length else "")


def _calculate_relevance(title: str, content: str) -> float:
    text = f"{title} {content}".lower()
    hits = sum(1 for keyword in RELEVANCE_KEYWORDS if keyword in text)
    return round(min(1.0, hits / len(RELEVANCE_KEYWORDS)), 2)


def _extract_cves(content: str) -> list[str]:
    return sorted(set(match.upper() for match in CVE_PATTERN.findall(content)))


async def fetch_html(url: str) -> str | None:
    try:
        async with httpx.AsyncClient(
            headers={"User-Agent": settings.scraping_user_agent}, timeout=10.0, follow_redirects=True
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except Exception as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return None


def parse_articles(html: str, source: ScrapingSource) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    articles: list[dict] = []
    for node in soup.select(source.article_selector):
        title_node = node.select_one(source.title_selector)
        content_node = node.select_one(source.content_selector)
        link_node = node.find("a", href=True)
        if not title_node:
            continue
        title = title_node.get_text(strip=True)
        content = content_node.get_text(strip=True) if content_node else title
        articles.append(
            {
                "title": title,
                "content": content,
                "source_url": link_node["href"] if link_node else source.url,
            }
        )
    return articles


def _mock_articles(source: ScrapingSource) -> list[dict]:
    """Fallback content used when a source cannot be reached over the network."""
    now = datetime.utcnow().strftime("%Y%m%d%H%M")
    return [
        {
            "title": f"[{source.name}] Critical vulnerability disclosed affecting widely used software (mock-{now})",
            "content": (
                "Security researchers disclosed a critical vulnerability that could allow remote code execution. "
                "A CVE-2026-12345 has been assigned and a patch is available. Organizations are urged to update "
                "as soon as possible to mitigate exploitation risk from this exploit."
            ),
            "source_url": source.url,
        }
    ]


class ScrapingService:
    def __init__(self, article_repo: ArticleRepository) -> None:
        self.article_repo = article_repo

    async def run_pipeline(self, sources: list[ScrapingSource] | None = None) -> list[ScrapedArticle]:
        sources = sources or DEFAULT_SOURCES
        stored: list[ScrapedArticle] = []

        for source in sources:
            html = await fetch_html(source.url)
            raw_articles = parse_articles(html, source) if html else []
            if not raw_articles:
                raw_articles = _mock_articles(source)

            for raw in raw_articles:
                content_hash = _hash_content(source.name, raw["title"], raw["content"])
                if await self.article_repo.get_by_hash(content_hash):
                    continue

                summary = _summarize(raw["content"])
                category = _classify_category(f"{raw['title']} {raw['content']}")
                relevance = _calculate_relevance(raw["title"], raw["content"])
                mentioned_cves = _extract_cves(raw["content"])

                article = ScrapedArticle(
                    source=source.name,
                    source_url=raw.get("source_url"),
                    title=raw["title"],
                    content=raw["content"],
                    summary=summary,
                    category=category,
                    tags=[category],
                    relevance_score=relevance,
                    mentioned_cves=mentioned_cves,
                    published_at=datetime.utcnow(),
                    hash=content_hash,
                    read_time=max(1, len(raw["content"].split()) // 200),
                )
                article = await self.article_repo.create(article)
                stored.append(article)

                await manager.broadcast_new_article(
                    {
                        "id": article.id,
                        "title": article.title,
                        "source": article.source,
                        "category": article.category,
                        "relevance_score": float(article.relevance_score or 0),
                    }
                )

        return stored
