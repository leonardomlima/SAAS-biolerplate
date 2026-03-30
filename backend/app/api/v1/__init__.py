from fastapi import APIRouter

from app.api.v1.endpoints import auth, billing, core_feature, health, organizations, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(users.router, prefix="/users")
api_router.include_router(organizations.router, prefix="/organizations")
api_router.include_router(billing.router, prefix="/billing")
api_router.include_router(core_feature.router, prefix="/core-feature")
