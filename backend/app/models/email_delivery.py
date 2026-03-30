from datetime import UTC, datetime

from sqlalchemy import JSON, Column
from sqlmodel import Field

from app.models.base import BaseModel


class EmailDelivery(BaseModel, table=True):
    template_key: str = Field(index=True)
    recipient_email: str = Field(index=True)
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    idempotency_key: str = Field(index=True, unique=True)
    provider_message_id: str | None = None
    status: str = Field(default="queued", index=True)
    attempts: int = 0
    last_error: str | None = None
    sent_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
