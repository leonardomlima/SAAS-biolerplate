from datetime import date
from uuid import UUID

from sqlmodel import Field

from app.models.base import BaseModel


class Subscription(BaseModel, table=True):
    organization_id: UUID
    asaas_subscription_id: str = Field(index=True)
    status: str = "PENDING"
    next_due_date: date | None = None
