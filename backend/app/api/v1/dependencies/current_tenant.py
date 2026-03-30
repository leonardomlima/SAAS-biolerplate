from uuid import UUID

from fastapi import Depends, HTTPException, Request, status

from app.api.v1.dependencies.current_user import get_current_user
from app.models.user import User


async def get_current_tenant(request: Request, current_user: User = Depends(get_current_user)) -> UUID:
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing X-Tenant-ID header")

    try:
        tenant_uuid = UUID(tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tenant id") from exc

    if tenant_uuid != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")

    return tenant_uuid
