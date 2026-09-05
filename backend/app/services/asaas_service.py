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

# Mapeamento de status de pagamento para status de subscription
_PAYMENT_TO_SUBSCRIPTION_STATUS: dict[str, str] = {
    "RECEIVED": "ACTIVE",
    "CONFIRMED": "ACTIVE",
    "PAYMENT_RECEIVED": "ACTIVE",
    "PAYMENT_CONFIRMED": "ACTIVE",
    "OVERDUE": "OVERDUE",
    "REFUNDED": "REFUNDED",
    "CANCELED": "CANCELED",
    "INACTIVE": "INACTIVE",
}


class AsaasService:
    def __init__(self) -> None:
        env_host = "sandbox" if settings.ASAAS_ENVIRONMENT == "sandbox" else "api"
        self.base_url = f"https://{env_host}.asaas.com/api/v3"
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
                    AsaasCustomer.is_deleted == False,
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
        """
        Retorna a URL do portal de autoatendimento do cliente no Asaas.
        O endpoint correto é GET /customers/{id}/portalUrl (sandbox e produção).
        """
        data = await self._request("GET", f"/customers/{customer_id}/portalUrl")
        # O Asaas retorna {"portalUrl": "https://..."}
        url = data.get("portalUrl") or data.get("url") or data.get("portal_url")
        if not url:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Portal URL not found in Asaas response: {data}",
            )
        return url

    @staticmethod
    def parse_due_date(value: str | None) -> date | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value).date()
        except (ValueError, TypeError):
            return None

    def _resolve_external_reference(self, raw_payload: dict) -> str | None:
        """
        Extrai o externalReference de qualquer tipo de evento Asaas.

        O campo pode estar em:
        - payload["subscription"]["externalReference"]  → eventos de assinatura
        - payload["payment"]["externalReference"]       → eventos de pagamento avulso
        - payload["externalReference"]                  → raramente na raiz
        """
        # 1. Tenta em subscription
        subscription_block = raw_payload.get("subscription") or {}
        ref = subscription_block.get("externalReference")
        if ref:
            return ref

        # 2. Tenta em payment
        payment_block = raw_payload.get("payment") or {}
        ref = payment_block.get("externalReference")
        if ref:
            return ref

        # 3. Tenta na raiz
        return raw_payload.get("externalReference")

    async def sync_subscription_from_webhook(self, session: AsyncSession, payload: dict) -> Subscription | None:
        """
        Sincroniza a subscription local com os dados do webhook.
        Suporta eventos de subscription e de payment (ex: PAYMENT_RECEIVED).
        """
        external_reference = self._resolve_external_reference(payload)
        if not external_reference:
            return None

        try:
            org_id = UUID(external_reference)
        except (ValueError, AttributeError):
            return None

        subscription = (
            await session.exec(
                select(Subscription).where(
                    Subscription.organization_id == org_id,
                    Subscription.is_deleted == False,
                )
            )
        ).first()
        if not subscription:
            return None

        event_type: str = payload.get("event", "")
        subscription_block = payload.get("subscription") or {}
        payment_block = payload.get("payment") or {}

        # Atualiza ID e data a partir do bloco de subscription, se disponível
        if subscription_block.get("id"):
            subscription.asaas_subscription_id = subscription_block["id"]
        if subscription_block.get("nextDueDate"):
            subscription.next_due_date = self.parse_due_date(subscription_block["nextDueDate"])

        # Determina novo status
        new_status: str | None = None

        # Prioridade 1: status explícito na subscription
        if subscription_block.get("status"):
            new_status = subscription_block["status"]
        # Prioridade 2: deduz pelo tipo de evento
        elif event_type in _PAYMENT_TO_SUBSCRIPTION_STATUS:
            new_status = _PAYMENT_TO_SUBSCRIPTION_STATUS[event_type]
        # Prioridade 3: status no bloco de pagamento (fallback)
        elif payment_block.get("status"):
            raw_pay_status = payment_block["status"]
            new_status = _PAYMENT_TO_SUBSCRIPTION_STATUS.get(raw_pay_status, raw_pay_status)

        if new_status:
            subscription.status = new_status

        subscription.last_synced_at = datetime.now(UTC)

        # Marca data de ativação / cancelamento
        if subscription.status in {"ACTIVE", "RECEIVED", "CONFIRMED"} and not subscription.activated_at:
            subscription.activated_at = datetime.now(UTC)
        if subscription.status in {"CANCELED", "INACTIVE"}:
            subscription.canceled_at = datetime.now(UTC)

        session.add(subscription)
        await session.commit()
        await session.refresh(subscription)
        return subscription
