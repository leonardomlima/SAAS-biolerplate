from uuid import UUID

from sqlmodel import Field

from app.models.base import BaseModel


class User(BaseModel, table=True):
    email: str = Field(index=True, unique=True)
    full_name: str | None = None
    hashed_password: str
    organization_id: UUID | None = None
