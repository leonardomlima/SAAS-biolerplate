from uuid import UUID

from sqlmodel import Field

from app.models.base import BaseModel


class AsaasCustomer(BaseModel, table=True):
    organization_id: UUID = Field(foreign_key="organization.id", index=True)
    asaas_customer_id: str = Field(index=True, unique=True)
    name: str
    email: str
    cpf_cnpj: str | None = None
