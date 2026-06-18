from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import CampaignStatus


class ThreatActorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    aliases: list | None
    country: str | None
    motivation: str | None
    ttps: list | None
    description: str | None


class CampaignOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    actor_id: int | None
    threat_score: float
    status: CampaignStatus
    first_seen: datetime | None
    last_seen: datetime | None
    created_at: datetime


class CampaignDetail(CampaignOut):
    actor: ThreatActorOut | None
    cve_ids: list[int]
    article_ids: list[int]


class GraphNode(BaseModel):
    id: str
    type: str
    label: str


class GraphEdge(BaseModel):
    source: str
    target: str


class CorrelationGraph(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class TimelineEvent(BaseModel):
    occurred_at: datetime
    type: str
    label: str
