from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.enums import AlertStatus


class AlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, alert_id: int) -> Alert | None:
        return await self.session.get(Alert, alert_id)

    async def list_for_user(self, user_id: int, status: AlertStatus | None = None) -> list[Alert]:
        query = select(Alert).where(Alert.user_id == user_id)
        if status is not None:
            query = query.where(Alert.status == status)
        query = query.order_by(Alert.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, alert: Alert) -> Alert:
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def acknowledge(self, alert: Alert) -> Alert:
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(alert)
        return alert
