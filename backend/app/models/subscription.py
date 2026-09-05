from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import DateTime
from sqlmodel import Field

from app.models.base import BaseModel, utc_now


class Subscription(BaseModel, table=True):
    organization_id: UUID = Field(foreign_key="organization.id", index=True)
    asaas_customer_id: str | None = Field(default=None, index=True)
    asaas_subscription_id: str | None = Field(default=None, index=True, unique=True)
    plan_id: str = Field(index=True)
    status: str = Field(default="PENDING", index=True)
    value: float = 0
    billing_cycle: str = Field(default="MONTHLY")
    next_due_date: date | None = None
    activated_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    canceled_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    last_synced_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )
