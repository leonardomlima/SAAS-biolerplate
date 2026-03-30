from app.crud.base import CRUDBase
from app.models.organization import Organization

crud_organization = CRUDBase[Organization](Organization)
