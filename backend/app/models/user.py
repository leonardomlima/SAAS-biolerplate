from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Field

from app.models.base import BaseModel


class User(BaseModel, table=True):
    email: str = Field(index=True, unique=True)
    full_name: str | None = None
    hashed_password: str
    organization_id: UUID | None = Field(default=None, foreign_key="organization.id")
    role: str = Field(default="member", index=True)
    is_active: bool = True
    email_verified: bool = False
    reset_password_token: str | None = None
    reset_password_expires_at: datetime | None = None
    email_verification_token: str | None = None
    refresh_token_version: int = 0
    last_login_at: datetime | None = None
