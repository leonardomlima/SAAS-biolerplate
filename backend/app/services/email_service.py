from datetime import UTC, datetime
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.models.email_delivery import EmailDelivery


class EmailService:
    def __init__(self) -> None:
        self.base_url = "https://api.brevo.com/v3"
        self.headers = {
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
        }

    async def _send_template(
        self,
        *,
        session: AsyncSession,
        tenant_id: str,
        template_key: str,
        to_email: str,
        template_id: int,
        params: dict,
        idempotency_key: str,
    ) -> None:
        if not settings.BREVO_API_KEY:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="BREVO API key missing")
        if template_id <= 0:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Template {template_key} not configured")

        existing = (
            await session.exec(select(EmailDelivery).where(EmailDelivery.idempotency_key == idempotency_key))
        ).first()
        if existing and existing.status == "sent":
            return

        delivery = existing or EmailDelivery(
            tenant_id=UUID(tenant_id),
            template_key=template_key,
            recipient_email=to_email,
            payload=params,
            idempotency_key=idempotency_key,
        )
        delivery.attempts += 1

        payload = {
            "sender": {"name": settings.BREVO_SENDER_NAME, "email": settings.BREVO_SENDER_EMAIL},
            "to": [{"email": to_email}],
            "templateId": template_id,
            "params": params,
        }

        async with httpx.AsyncClient(base_url=self.base_url, timeout=20) as client:
            response = await client.post("/smtp/email", headers=self.headers, json=payload)

        if response.status_code >= 400:
            delivery.status = "failed"
            delivery.last_error = response.text
            session.add(delivery)
            await session.commit()
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Brevo delivery failed")

        data = response.json()
        delivery.status = "sent"
        delivery.provider_message_id = data.get("messageId")
        delivery.sent_at = datetime.now(UTC)
        delivery.last_error = None
        session.add(delivery)
        await session.commit()

    async def send_welcome_email(self, session: AsyncSession, email: str, tenant_id: str, full_name: str | None) -> None:
        await self._send_template(
            session=session,
            tenant_id=tenant_id,
            template_key="welcome",
            to_email=email,
            template_id=settings.BREVO_TEMPLATE_WELCOME_ID,
            params={"first_name": full_name or "", "tenant_id": tenant_id},
            idempotency_key=f"welcome:{tenant_id}:{email}",
        )

    async def send_password_reset(self, session: AsyncSession, email: str, reset_token: str, tenant_id: str) -> None:
        await self._send_template(
            session=session,
            tenant_id=tenant_id,
            template_key="reset_password",
            to_email=email,
            template_id=settings.BREVO_TEMPLATE_RESET_ID,
            params={"reset_token": reset_token, "tenant_id": tenant_id},
            idempotency_key=f"reset:{tenant_id}:{email}:{reset_token}",
        )

    async def send_organization_invite(
        self,
        session: AsyncSession,
        email: str,
        organization_name: str,
        tenant_id: str,
    ) -> None:
        await self._send_template(
            session=session,
            tenant_id=tenant_id,
            template_key="invite",
            to_email=email,
            template_id=settings.BREVO_TEMPLATE_INVITE_ID,
            params={"organization_name": organization_name, "tenant_id": tenant_id},
            idempotency_key=f"invite:{tenant_id}:{email}:{organization_name}",
        )
