from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.dependencies.current_tenant import get_current_tenant
from app.api.v1.dependencies.current_user import get_current_user
from app.core.config import settings
from app.core.database import get_session
from app.models.asaas_webhook_event import AsaasWebhookEvent
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.billing import AsaasWebhookPayload, CheckoutRequest, Plan, PortalRequest, SubscriptionRead
from app.services.asaas_service import AsaasService
from app.services.audit_service import write_audit_log

router = APIRouter()

PLANS = {
    "starter": {"id": "starter", "name": "Starter", "amount": 49.0, "billing_cycle": "MONTHLY"},
    "growth": {"id": "growth", "name": "Growth", "amount": 149.0, "billing_cycle": "MONTHLY"},
    "scale": {"id": "scale", "name": "Scale", "amount": 399.0, "billing_cycle": "MONTHLY"},
}


@router.get("/plans", response_model=list[Plan])
async def plans() -> list[Plan]:
    return [Plan(**plan) for plan in PLANS.values()]


@router.post("/checkout")
async def checkout(
    payload: CheckoutRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    tenant_id=Depends(get_current_tenant),
) -> dict[str, str]:
    plan = PLANS.get(payload.plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid plan")

    organization = await session.get(Organization, current_user.organization_id)
    if not organization or organization.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    asaas_service = AsaasService()
    customer = await asaas_service.ensure_customer(session, organization, current_user)
    remote_subscription = await asaas_service.create_checkout(customer.asaas_customer_id, plan, str(organization.id))

    subscription = (
        await session.exec(
            select(Subscription).where(
                Subscription.organization_id == organization.id,
                Subscription.is_deleted.is_(False),
            )
        )
    ).first()
    if not subscription:
        subscription = Subscription(
            tenant_id=tenant_id,
            organization_id=organization.id,
            plan_id=plan["id"],
            value=plan["amount"],
            billing_cycle=plan["billing_cycle"],
            asaas_customer_id=customer.asaas_customer_id,
            asaas_subscription_id=remote_subscription["subscription_id"],
            status=remote_subscription["status"],
            next_due_date=AsaasService.parse_due_date(remote_subscription.get("next_due_date")),
        )
    else:
        subscription.plan_id = plan["id"]
        subscription.value = plan["amount"]
        subscription.billing_cycle = plan["billing_cycle"]
        subscription.asaas_customer_id = customer.asaas_customer_id
        subscription.asaas_subscription_id = remote_subscription["subscription_id"]
        subscription.status = remote_subscription["status"]
        subscription.next_due_date = AsaasService.parse_due_date(remote_subscription.get("next_due_date"))
        subscription.last_synced_at = datetime.now(UTC)

    session.add(subscription)
    await session.commit()

    await write_audit_log(
        session,
        tenant_id=current_user.tenant_id,
        actor_user_id=current_user.id,
        action="billing.checkout",
        entity_type="subscription",
        entity_id=str(subscription.id),
        details=f"plan={plan['id']} status={subscription.status}",
    )

    return {"subscription_id": remote_subscription["subscription_id"], "status": remote_subscription["status"]}


@router.post("/portal")
async def portal(
    payload: PortalRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    tenant_id=Depends(get_current_tenant),
) -> dict[str, str]:
    subscription = (
        await session.exec(
            select(Subscription).where(
                Subscription.organization_id == current_user.organization_id,
                Subscription.tenant_id == tenant_id,
                Subscription.is_deleted.is_(False),
            )
        )
    ).first()
    if not subscription or not subscription.asaas_customer_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not initialized")

    asaas_service = AsaasService()
    portal_url = await asaas_service.create_customer_portal(subscription.asaas_customer_id)
    return {"portal_url": portal_url}


@router.post("/webhook")
async def webhook(
    payload: AsaasWebhookPayload,
    session: AsyncSession = Depends(get_session),
    asaas_access_token: str | None = Header(default=None),
) -> dict:
    if settings.ASAAS_WEBHOOK_SECRET and asaas_access_token != settings.ASAAS_WEBHOOK_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook token")

    raw_payload = payload.model_dump(mode="json")
    external_reference = (raw_payload.get("subscription") or {}).get("externalReference")
    organization = await session.get(Organization, external_reference) if external_reference else None
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found for webhook")

    event = AsaasWebhookEvent(
        tenant_id=organization.tenant_id,
        organization_id=organization.id,
        event=payload.event,
        external_id=payload.id,
        payload=raw_payload,
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)

    asaas_service = AsaasService()
    try:
        synced = await asaas_service.sync_subscription_from_webhook(session, raw_payload)
        event.processing_status = "processed"
        event.processed_at = datetime.now(UTC)
        session.add(event)
        await session.commit()
    except Exception as exc:
        event.processing_status = "failed"
        event.failure_reason = str(exc)
        session.add(event)
        await session.commit()
        raise

    if synced and organization:
        await write_audit_log(
            session,
            tenant_id=organization.tenant_id,
            actor_user_id=None,
            action="billing.webhook_processed",
            entity_type="subscription",
            entity_id=str(synced.id),
            details=payload.event,
        )

    return {"ok": True, "event": payload.event, "subscription_synced": bool(synced)}


@router.get("/subscription", response_model=SubscriptionRead)
async def subscription(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    tenant_id=Depends(get_current_tenant),
) -> SubscriptionRead:
    subscription_row = (
        await session.exec(
            select(Subscription).where(
                Subscription.organization_id == current_user.organization_id,
                Subscription.tenant_id == tenant_id,
                Subscription.is_deleted.is_(False),
            )
        )
    ).first()
    if not subscription_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    return SubscriptionRead.model_validate(subscription_row)
