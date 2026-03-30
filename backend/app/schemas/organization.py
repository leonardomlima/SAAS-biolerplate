from uuid import UUID

from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str


class OrganizationRead(BaseModel):
    id: UUID
    name: str
