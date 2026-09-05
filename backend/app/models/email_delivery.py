from datetime import UTC, datetime

from sqlalchemy import JSON, Column, DateTime
from sqlmodel import Field

from app.models.base import BaseModel, utc_now


class EmailDelivery(BaseModel, table=True):
    template_key: str = Field(index=True)
    recipient_email: str = Field(index=True)
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    idempotency_key: str = Field(index=True, unique=True)
    provider_message_id: str | None = None
    status: str = Field(default="queued", index=True)
    attempts: int = 0
    last_error: str | None = None
    sent_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )
