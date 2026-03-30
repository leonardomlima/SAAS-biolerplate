from uuid import UUID

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID")
        request.state.tenant_id = tenant_id
        return await call_next(request)


def get_tenant_id(request: Request) -> UUID | None:
    tenant_id = getattr(request.state, "tenant_id", None)
    return UUID(tenant_id) if tenant_id else None
