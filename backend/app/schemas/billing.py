from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict


class Plan(BaseModel):
    id: str
    name: str
    amount: float
    billing_cycle: str


class CheckoutRequest(BaseModel):
    plan_id: str


class PortalRequest(BaseModel):
    return_url: str | None = None


class SubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    asaas_subscription_id: str | None = None
    plan_id: str
    value: float
    next_due_date: date | None = None


class AsaasWebhookPayload(BaseModel):
    """
    Payload enviado pelo Asaas no webhook.

    O Asaas pode adicionar campos extras; usamos model_config extra='allow'
    para não rejeitar payloads com campos desconhecidos.
    """

    model_config = ConfigDict(extra="allow")

    event: str
    id: str | None = None
    payment: dict[str, Any] | None = None
    subscription: dict[str, Any] | None = None
