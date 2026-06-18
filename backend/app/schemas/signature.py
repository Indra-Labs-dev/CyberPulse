from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import SignatureType


class YaraGenerateRequest(BaseModel):
    name: str
    description: str | None = None
    strings: list[str] = []
    hashes: list[str] = []
    tags: list[str] = []


class SigmaGenerateRequest(BaseModel):
    name: str
    description: str | None = None
    log_source: dict = {}
    detection_selection: dict = {}
    level: str = "medium"


class SignatureValidateRequest(BaseModel):
    type: SignatureType
    rule_text: str


class SignatureValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = []


class SignatureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: SignatureType
    rule_text: str
    source_description: str | None
    is_valid: bool
    created_by: int
    created_at: datetime
