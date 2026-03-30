from datetime import UTC, date, datetime
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.models.asaas_customer import AsaasCustomer
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.user import User


class AsaasService:
    def __init__(self) -> None:
        env_host = "api" if settings.ASAAS_ENVIRONMENT == "production" else "sandbox"
        self.base_url = f"https://{env_host}.asaas.com/v3"
        self.headers = {"access_token": settings.ASAAS_API_KEY, "Content-Type": "application/json"}

    async def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        if not settings.ASAAS_API_KEY:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="ASAAS API key missing")

        async with httpx.AsyncClient(base_url=self.base_url, timeout=20) as client:
            response = await client.request(method, path, headers=self.headers, json=payload)

        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Asaas error: {response.text}")
        return response.json()

    async def ensure_customer(self, session: AsyncSession, organization: Organization, user: User) -> AsaasCustomer:
        customer = (
            await session.exec(
                select(AsaasCustomer).where(
                    AsaasCustomer.organization_id == organization.id,
                    AsaasCustomer.is_deleted.is_(False),
                )
            )
        ).first()
        if customer:
            return customer

        payload = {
            "name": organization.name,
            "email": user.email,
            "externalReference": str(organization.id),
            "notificationDisabled": False,
        }
        data = await self._request("POST", "/customers", payload)
        customer = AsaasCustomer(
            tenant_id=organization.tenant_id,
            organization_id=organization.id,
            asaas_customer_id=data["id"],
            name=organization.name,
            email=user.email,
        )
        session.add(customer)
        await session.commit()
        await session.refresh(customer)
        return customer

    async def create_checkout(self, customer_id: str, plan: dict, external_reference: str) -> dict:
        payload = {
            "customer": customer_id,
            "billingType": "UNDEFINED",
            "chargeType": "RECURRENT",
            "name": plan["name"],
            "description": f"Plano {plan['name']}",
            "value": plan["amount"],
            "cycle": plan["billing_cycle"],
            "externalReference": external_reference,
        }
        subscription = await self._request("POST", "/subscriptions", payload)
        return {
            "subscription_id": subscription["id"],
            "status": subscription.get("status", "PENDING"),
            "next_due_date": subscription.get("nextDueDate"),
        }

    async def create_customer_portal(self, customer_id: str) -> str:
        portal_data = await self._request("POST", "/customerPortal/session", {"customer": customer_id})
        return portal_data["url"]

    @staticmethod
    def parse_due_date(value: str | None) -> date | None:
        if not value:
            return None
        return datetime.fromisoformat(value).date()

    async def sync_subscription_from_webhook(self, session: AsyncSession, payload: dict) -> Subscription | None:
        subscription_payload = payload.get("subscription") or {}
        external_reference = subscription_payload.get("externalReference")
        if not external_reference:
            return None

        org_id = UUID(external_reference)
        subscription = (
            await session.exec(
                select(Subscription).where(
                    Subscription.organization_id == org_id,
                    Subscription.is_deleted.is_(False),
                )
            )
        ).first()
        if not subscription:
            return None

        subscription.asaas_subscription_id = subscription_payload.get("id", subscription.asaas_subscription_id)
        subscription.status = subscription_payload.get("status", subscription.status)
        subscription.next_due_date = self.parse_due_date(subscription_payload.get("nextDueDate"))
        subscription.last_synced_at = datetime.now(UTC)
        if subscription.status in {"ACTIVE", "RECEIVED"} and not subscription.activated_at:
            subscription.activated_at = datetime.now(UTC)
        if subscription.status in {"CANCELED", "INACTIVE"}:
            subscription.canceled_at = datetime.now(UTC)

        session.add(subscription)
        await session.commit()
        await session.refresh(subscription)
        return subscription
