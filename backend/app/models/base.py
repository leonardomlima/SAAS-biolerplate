from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """Return UTC datetime with timezone info for TIMESTAMP WITH TIME ZONE compatibility."""
    return datetime.now(UTC)


class BaseModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(index=True)
    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )
    updated_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )
