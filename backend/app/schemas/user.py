from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    email: EmailStr
    password: str
    full_name: str | None = None
    tenant_id: UUID


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None = None
