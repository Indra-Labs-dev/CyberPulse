from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScrapedArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    source_url: str | None
    title: str
    slug: str | None
    author: str | None
    summary: str | None
    category: str | None
    tags: list | None
    relevance_score: float | None
    mentioned_cves: list | None
    published_at: datetime | None
    scraped_at: datetime
    image_url: str | None
    read_time: int | None
    is_favorite: bool
    is_read: bool


class ScrapedArticleDetail(ScrapedArticleOut):
    content: str | None


class ArticleFilters(BaseModel):
    source: str | None = None
    category: str | None = None
    search: str | None = None
    is_favorite: bool | None = None
    is_read: bool | None = None
