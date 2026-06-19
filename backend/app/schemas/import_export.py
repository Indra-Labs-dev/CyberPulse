from pydantic import BaseModel


class ImportResult(BaseModel):
    imported: int
    updated: int
    errors: list[str] = []


class BackupBundle(BaseModel):
    version: str = "1.0"
    cves: list[dict]
    watchlists: list[dict]
    articles: list[dict]
