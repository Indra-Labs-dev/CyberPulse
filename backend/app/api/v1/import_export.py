from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.repositories.article_repo import ArticleRepository
from app.repositories.cve_repo import CVERepository
from app.repositories.watchlist_repo import WatchlistRepository
from app.schemas.cve import CVEFilters
from app.schemas.import_export import BackupBundle, ImportResult
from app.services.import_export_service import ImportExportService

router = APIRouter(prefix="/import-export", tags=["import-export"])


def get_import_export_service(db: AsyncSession = Depends(get_db)) -> ImportExportService:
    return ImportExportService(CVERepository(db), WatchlistRepository(db), ArticleRepository(db))


@router.post(
    "/import/cves/json",
    response_model=ImportResult,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def import_cves_json(
    file: UploadFile = File(...), service: ImportExportService = Depends(get_import_export_service)
) -> ImportResult:
    raw = await file.read()
    return await service.import_cves_json(raw)


@router.post(
    "/import/cves/csv",
    response_model=ImportResult,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def import_cves_csv(
    file: UploadFile = File(...), service: ImportExportService = Depends(get_import_export_service)
) -> ImportResult:
    raw = await file.read()
    return await service.import_cves_csv(raw)


@router.get("/export/cves")
async def export_cves(
    format: str = "json", service: ImportExportService = Depends(get_import_export_service)
) -> PlainTextResponse:
    filters = CVEFilters()
    exporters = {
        "json": (service.export_json, "application/json", "json"),
        "csv": (service.export_csv, "text/csv", "csv"),
        "xml": (service.export_xml, "application/xml", "xml"),
        "stix": (service.export_stix, "application/json", "json"),
        "misp": (service.export_misp, "application/json", "json"),
        "openioc": (service.export_openioc, "application/xml", "xml"),
    }
    exporter, media_type, extension = exporters.get(format, exporters["json"])
    content = await exporter(filters)
    return PlainTextResponse(
        content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="cyberpulse_cves_{format}.{extension}"'},
    )


@router.get("/backup", response_model=BackupBundle)
async def backup(service: ImportExportService = Depends(get_import_export_service)) -> BackupBundle:
    return await service.backup()


@router.post(
    "/restore",
    response_model=ImportResult,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def restore(
    bundle: BackupBundle, service: ImportExportService = Depends(get_import_export_service)
) -> ImportResult:
    return await service.restore_cves(bundle)
