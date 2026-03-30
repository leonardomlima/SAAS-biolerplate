from pydantic import BaseModel


class Plan(BaseModel):
    id: str
    name: str
    amount: float


class CheckoutRequest(BaseModel):
    plan_id: str


class SubscriptionRead(BaseModel):
    status: str
    asaas_subscription_id: str | None = None


class WebhookEvent(BaseModel):
    event: str
    payment_id: str | None = None


class AsaasWebhookPayload(BaseModel):
    event: str
    payment: dict | None = None
