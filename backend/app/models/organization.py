from sqlmodel import Field

from app.models.base import BaseModel


class Organization(BaseModel, table=True):
    name: str = Field(index=True)
