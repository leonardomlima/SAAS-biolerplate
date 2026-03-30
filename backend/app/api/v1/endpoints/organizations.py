from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.api.v1.dependencies.current_user import get_current_user
from app.core.database import get_session
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationRead

router = APIRouter()


@router.get("/", response_model=list[OrganizationRead])
async def list_organizations(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[OrganizationRead]:
    organizations = (
        await session.exec(
            select(Organization).where(Organization.tenant_id == current_user.tenant_id, Organization.is_deleted.is_(False))
        )
    ).all()
    return [OrganizationRead(id=org.id, name=org.name) for org in organizations]


@router.post("/", response_model=OrganizationRead)
async def create_organization(
    payload: OrganizationCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> OrganizationRead:
    if current_user.role not in {"owner", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    organization = Organization(id=uuid4(), tenant_id=current_user.tenant_id, name=payload.name)
    session.add(organization)
    await session.commit()
    await session.refresh(organization)
    return OrganizationRead(id=organization.id, name=organization.name)
