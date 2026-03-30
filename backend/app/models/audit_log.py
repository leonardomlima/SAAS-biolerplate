from uuid import UUID

from sqlmodel import Field

from app.models.base import BaseModel


class AuditLog(BaseModel, table=True):
    actor_user_id: UUID | None = None
    action: str = Field(index=True)
    entity_type: str
    entity_id: str
    details: str | None = None
