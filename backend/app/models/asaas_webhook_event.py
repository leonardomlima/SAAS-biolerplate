from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import JSON, Column, DateTime
from sqlmodel import Field

from app.models.base import BaseModel, utc_now


class AsaasWebhookEvent(BaseModel, table=True):
    organization_id: UUID | None = Field(
        default=None, foreign_key="organization.id", index=True
    )
    event: str = Field(index=True)
    # external_id não é mais UNIQUE para tolerar reentrega de eventos pelo Asaas
    external_id: str | None = Field(default=None, index=True)
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    processed_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    processing_status: str = Field(default="pending", index=True)
    failure_reason: str | None = None
    received_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )
