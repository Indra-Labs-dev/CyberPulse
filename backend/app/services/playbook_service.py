from __future__ import annotations

from datetime import datetime

import httpx

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.cve import CVE
from app.models.enums import AlertType, PlaybookTriggerType, ReportType, ScanStatus, Severity
from app.models.playbook import Playbook, PlaybookRun
from app.repositories.alert_repo import AlertRepository
from app.repositories.cve_repo import CVERepository
from app.repositories.incident_repo import IncidentRepository
from app.repositories.playbook_repo import PlaybookRepository
from app.repositories.report_repo import ReportRepository
from app.schemas.alert import AlertCreate
from app.schemas.incident import IncidentCreate
from app.schemas.playbook import PlaybookCreate, PlaybookTemplate, PlaybookUpdate
from app.schemas.report import ReportCreate
from app.services.alert_service import AlertService
from app.services.incident_service import IncidentService
from app.services.report_service import ReportService

logger = get_logger(__name__)

PLAYBOOK_TEMPLATES = [
    PlaybookTemplate(
        name="Réponse Ransomware",
        description="Crée un incident critique et génère un rapport dès qu'une CVE critique liée à un ransomware apparaît.",
        trigger_type=PlaybookTriggerType.NEW_CRITICAL_CVE,
        trigger_config={"min_cvss": 8.5},
        actions=[
            {"type": "CREATE_INCIDENT", "config": {"severity": "CRITICAL"}},
            {"type": "GENERATE_REPORT", "config": {"title": "Rapport d'urgence ransomware"}},
            {"type": "SEND_ALERT", "config": {"message": "Playbook Réponse Ransomware déclenché"}},
        ],
    ),
    PlaybookTemplate(
        name="Patch Tuesday",
        description="Génère automatiquement un rapport de synthèse pour toute CVE haute sévérité détectée.",
        trigger_type=PlaybookTriggerType.NEW_CRITICAL_CVE,
        trigger_config={"min_cvss": 7.0},
        actions=[{"type": "GENERATE_REPORT", "config": {"title": "Synthèse Patch Tuesday"}}],
    ),
    PlaybookTemplate(
        name="Alerte Exploit Public",
        description="Notifie l'équipe dès qu'un exploit public est détecté pour une CVE suivie.",
        trigger_type=PlaybookTriggerType.NEW_EXPLOIT,
        trigger_config={},
        actions=[{"type": "SEND_ALERT", "config": {"message": "Un exploit public est désormais disponible"}}],
    ),
]


class PlaybookService:
    def __init__(
        self,
        repo: PlaybookRepository,
        alert_repo: AlertRepository,
        incident_repo: IncidentRepository,
        report_repo: ReportRepository,
        cve_repo: CVERepository,
    ) -> None:
        self.repo = repo
        self.alert_service = AlertService(alert_repo)
        self.incident_service = IncidentService(incident_repo)
        self.report_service = ReportService(report_repo, cve_repo)

    def list_templates(self) -> list[PlaybookTemplate]:
        return PLAYBOOK_TEMPLATES

    async def get(self, playbook_id: int) -> Playbook:
        playbook = await self.repo.get_by_id(playbook_id)
        if not playbook:
            raise NotFoundError("Playbook not found")
        return playbook

    async def list(self, active_only: bool = False) -> list[Playbook]:
        return await self.repo.list(active_only)

    async def create(self, user_id: int, data: PlaybookCreate) -> Playbook:
        playbook = Playbook(
            name=data.name,
            description=data.description,
            trigger_type=data.trigger_type,
            trigger_config=data.trigger_config,
            actions=[a.model_dump() for a in data.actions],
            is_active=data.is_active,
            created_by=user_id,
        )
        return await self.repo.create(playbook)

    async def update(self, playbook_id: int, data: PlaybookUpdate) -> Playbook:
        playbook = await self.get(playbook_id)
        update_data = data.model_dump(exclude_unset=True)
        if "actions" in update_data and update_data["actions"] is not None:
            update_data["actions"] = [a if isinstance(a, dict) else a.model_dump() for a in update_data["actions"]]
        for key, value in update_data.items():
            setattr(playbook, key, value)
        return await self.repo.update(playbook)

    async def delete(self, playbook_id: int) -> None:
        playbook = await self.get(playbook_id)
        await self.repo.delete(playbook)

    async def list_runs(self, playbook_id: int) -> list[PlaybookRun]:
        return await self.repo.list_runs(playbook_id)

    async def run(self, playbook_id: int, user_id: int, trigger_source: str = "MANUAL") -> PlaybookRun:
        playbook = await self.get(playbook_id)
        run = await self.repo.create_run(
            PlaybookRun(playbook_id=playbook.id, trigger_source=trigger_source, status=ScanStatus.RUNNING)
        )

        log_lines: list[str] = [f"Démarrage du playbook « {playbook.name} » (source: {trigger_source})"]
        success = True

        for action in playbook.actions:
            action_type = action.get("type")
            config = action.get("config", {})
            try:
                await self._execute_action(action_type, config, user_id, playbook)
                log_lines.append(f"[OK] Action {action_type} exécutée")
            except Exception as exc:
                success = False
                log_lines.append(f"[ERREUR] Action {action_type} a échoué: {exc}")
                logger.exception("Playbook action failed: %s", action_type)

        run.status = ScanStatus.COMPLETED if success else ScanStatus.FAILED
        run.log = "\n".join(log_lines)
        run.finished_at = datetime.utcnow()
        return await self.repo.update_run(run)

    async def _execute_action(self, action_type: str, config: dict, user_id: int, playbook: Playbook) -> None:
        if action_type == "SEND_ALERT":
            await self.alert_service.create(
                AlertCreate(
                    user_id=user_id,
                    type=AlertType.SYSTEM,
                    severity=Severity(config.get("severity", "MEDIUM")),
                    message=config.get("message", f"Playbook {playbook.name} exécuté"),
                )
            )
        elif action_type == "CREATE_INCIDENT":
            await self.incident_service.create(
                user_id,
                IncidentCreate(
                    title=config.get("title", f"Incident généré par {playbook.name}"),
                    description=config.get("description"),
                    severity=Severity(config.get("severity", "MEDIUM")),
                ),
            )
        elif action_type == "GENERATE_REPORT":
            await self.report_service.generate(
                user_id,
                ReportCreate(title=config.get("title", f"Rapport — {playbook.name}"), type=ReportType.CVE),
            )
        elif action_type == "WEBHOOK":
            url = config.get("url")
            if url:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(url, json={"playbook": playbook.name, **config.get("payload", {})})
        elif action_type == "LOG":
            logger.info("Playbook log action: %s", config.get("message", ""))
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    async def evaluate_cve_trigger(self, cve: CVE) -> list[PlaybookRun]:
        """Auto-runs playbooks configured for NEW_CRITICAL_CVE / NEW_EXPLOIT
        whenever a CVE matching their trigger_config is synced, e.g.
        `{"min_cvss": 8.5}`. Called from the scheduled CVE sync job.
        """
        runs: list[PlaybookRun] = []

        if cve.severity in (Severity.CRITICAL, Severity.HIGH):
            for playbook in await self.repo.list_by_trigger(PlaybookTriggerType.NEW_CRITICAL_CVE):
                min_cvss = playbook.trigger_config.get("min_cvss", 0) if playbook.trigger_config else 0
                if float(cve.cvss_score or 0) >= min_cvss:
                    runs.append(await self.run(playbook.id, playbook.created_by, trigger_source=f"CVE:{cve.cve_id}"))

        if cve.exploits:
            for playbook in await self.repo.list_by_trigger(PlaybookTriggerType.NEW_EXPLOIT):
                runs.append(await self.run(playbook.id, playbook.created_by, trigger_source=f"EXPLOIT:{cve.cve_id}"))

        return runs
