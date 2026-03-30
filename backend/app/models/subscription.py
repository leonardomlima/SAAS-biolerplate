from datetime import UTC, date, datetime
from uuid import UUID

from sqlmodel import Field

from app.models.base import BaseModel


class Subscription(BaseModel, table=True):
    organization_id: UUID = Field(foreign_key="organization.id", index=True)
    asaas_customer_id: str | None = Field(default=None, index=True)
    asaas_subscription_id: str | None = Field(default=None, index=True, unique=True)
    plan_id: str = Field(index=True)
    status: str = Field(default="PENDING", index=True)
    value: float = 0
    billing_cycle: str = Field(default="MONTHLY")
    next_due_date: date | None = None
    activated_at: datetime | None = None
    canceled_at: datetime | None = None
    last_synced_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
