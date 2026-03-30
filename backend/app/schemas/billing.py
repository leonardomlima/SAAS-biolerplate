from datetime import date

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
    event: str
    id: str | None = None
    payment: dict | None = None
    subscription: dict | None = None
