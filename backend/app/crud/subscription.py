from app.crud.base import CRUDBase
from app.models.subscription import Subscription

crud_subscription = CRUDBase[Subscription](Subscription)
