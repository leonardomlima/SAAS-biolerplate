from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.api.v1.dependencies.current_tenant import get_current_tenant
from app.api.v1.dependencies.current_user import get_current_user
from app.core.database import get_session
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter()


@router.get("/", response_model=list[UserRead])
async def list_users(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    tenant_id=Depends(get_current_tenant),
) -> list[UserRead]:
    statement = (
        select(User)
        .where(User.tenant_id == tenant_id, User.is_deleted.is_(False))
        .offset(offset)
        .limit(limit)
    )
    users = (await session.exec(statement)).all()
    return [UserRead(id=user.id, email=user.email, full_name=user.full_name) for user in users]


@router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead(id=current_user.id, email=current_user.email, full_name=current_user.full_name)
