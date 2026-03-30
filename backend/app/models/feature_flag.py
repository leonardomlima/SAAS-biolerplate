from sqlmodel import Field

from app.models.base import BaseModel


class FeatureFlag(BaseModel, table=True):
    key: str = Field(index=True, unique=True)
    enabled: bool = False
