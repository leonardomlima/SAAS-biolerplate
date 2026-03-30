from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import JSON, Column
from sqlmodel import Field

from app.models.base import BaseModel


class AsaasWebhookEvent(BaseModel, table=True):
    organization_id: UUID | None = Field(default=None, foreign_key="organization.id", index=True)
    event: str = Field(index=True)
    external_id: str | None = Field(default=None, index=True, unique=True)
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    processed_at: datetime | None = None
    processing_status: str = Field(default="pending", index=True)
    failure_reason: str | None = None
    received_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
