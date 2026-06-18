from fastapi import APIRouter, Depends, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import SignatureType, UserRole
from app.models.user import User
from app.repositories.signature_repo import SignatureRepository
from app.schemas.signature import (
    SigmaGenerateRequest,
    SignatureOut,
    SignatureValidateRequest,
    SignatureValidationResult,
    YaraGenerateRequest,
)
from app.services.signature_service import SignatureService

router = APIRouter(prefix="/signatures", tags=["signatures"])


def get_signature_service(db: AsyncSession = Depends(get_db)) -> SignatureService:
    return SignatureService(SignatureRepository(db))


@router.get("", response_model=list[SignatureOut])
async def list_signatures(
    type: SignatureType | None = None, service: SignatureService = Depends(get_signature_service)
) -> list[SignatureOut]:
    signatures = await service.list(type)
    return [SignatureOut.model_validate(s) for s in signatures]


@router.post(
    "/generate/yara",
    response_model=SignatureOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def generate_yara(
    data: YaraGenerateRequest,
    current_user: User = Depends(get_current_user),
    service: SignatureService = Depends(get_signature_service),
) -> SignatureOut:
    rule_text = service.generate_yara(data)
    signature = await service.save(current_user.id, data.name, SignatureType.YARA, rule_text, data.description)
    return SignatureOut.model_validate(signature)


@router.post(
    "/generate/sigma",
    response_model=SignatureOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def generate_sigma(
    data: SigmaGenerateRequest,
    current_user: User = Depends(get_current_user),
    service: SignatureService = Depends(get_signature_service),
) -> SignatureOut:
    rule_text = service.generate_sigma(data)
    signature = await service.save(current_user.id, data.name, SignatureType.SIGMA, rule_text, data.description)
    return SignatureOut.model_validate(signature)


@router.post("/validate", response_model=SignatureValidationResult)
async def validate_signature(
    data: SignatureValidateRequest, service: SignatureService = Depends(get_signature_service)
) -> SignatureValidationResult:
    return service.validate(data.type, data.rule_text)


@router.delete(
    "/{signature_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def delete_signature(signature_id: int, service: SignatureService = Depends(get_signature_service)) -> None:
    await service.delete(signature_id)


@router.get("/{signature_id}/export")
async def export_signature(
    signature_id: int, service: SignatureService = Depends(get_signature_service)
) -> PlainTextResponse:
    signature = await service.get(signature_id)
    extension = "yar" if signature.type == SignatureType.YARA else "yml"
    return PlainTextResponse(
        signature.rule_text,
        headers={"Content-Disposition": f'attachment; filename="{signature.name}.{extension}"'},
    )
