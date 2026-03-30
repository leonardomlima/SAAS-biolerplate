from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.background.tasks import send_transactional_email_task
from app.core.database import get_session
from app.core.limiter import limiter
from app.core.security import create_access_token, create_refresh_token, decode_token, get_password_hash, verify_password
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import (
    ConfirmResetPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    Token,
    VerifyEmailRequest,
)
from app.services.audit_service import write_audit_log

router = APIRouter()
FAILED_LOGINS: dict[str, tuple[int, datetime]] = {}


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> Token:
    blocked = FAILED_LOGINS.get(payload.email)
    if blocked and blocked[0] >= 5 and blocked[1] > datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many failed attempts")

    user = (await session.exec(select(User).where(User.email == payload.email, User.is_deleted.is_(False)))).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        count = (blocked[0] + 1) if blocked else 1
        FAILED_LOGINS[payload.email] = (count, datetime.now(UTC) + timedelta(minutes=15))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    FAILED_LOGINS.pop(payload.email, None)

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")

    user.last_login_at = datetime.now(UTC)
    session.add(user)
    await session.commit()

    await write_audit_log(
        session,
        tenant_id=user.tenant_id,
        actor_user_id=user.id,
        action="auth.login",
        entity_type="user",
        entity_id=str(user.id),
    )

    token_extra = {"tenant_id": str(user.tenant_id), "rtv": user.refresh_token_version}
    return Token(
        access_token=create_access_token(str(user.id), token_extra),
        refresh_token=create_refresh_token(str(user.id), token_extra),
    )


@router.post("/register", response_model=Token)
@limiter.limit("5/minute")
async def register(request: Request, payload: RegisterRequest, session: AsyncSession = Depends(get_session)) -> Token:
    existing_user = (await session.exec(select(User).where(User.email == payload.email))).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    tenant_id = uuid4()
    organization = Organization(id=tenant_id, tenant_id=tenant_id, name=payload.organization_name or payload.email)
    user = User(
        tenant_id=tenant_id,
        organization_id=organization.id,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role="owner",
        email_verification_token=token_urlsafe(32),
    )

    session.add(organization)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    send_transactional_email_task.delay(  # pyright: ignore[reportFunctionMemberAccess]
        "welcome",
        email=user.email,
        tenant_id=str(user.tenant_id),
        full_name=user.full_name,
    )

    await write_audit_log(
        session,
        tenant_id=user.tenant_id,
        actor_user_id=user.id,
        action="auth.register",
        entity_type="user",
        entity_id=str(user.id),
    )

    token_extra = {"tenant_id": str(user.tenant_id), "rtv": user.refresh_token_version}
    return Token(
        access_token=create_access_token(str(user.id), token_extra),
        refresh_token=create_refresh_token(str(user.id), token_extra),
    )


@router.post("/refresh", response_model=Token)
@limiter.limit("20/minute")
async def refresh(request: Request, payload: RefreshRequest, session: AsyncSession = Depends(get_session)) -> Token:
    try:
        token_data = decode_token(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    if token_data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    try:
        user_id = UUID(token_data["sub"])
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    user = await session.get(User, user_id)
    if not user or not user.is_active or user.is_deleted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User unavailable")

    if token_data.get("rtv") != user.refresh_token_version:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

    token_extra = {"tenant_id": str(user.tenant_id), "rtv": user.refresh_token_version}
    return Token(
        access_token=create_access_token(str(user.id), token_extra),
        refresh_token=create_refresh_token(str(user.id), token_extra),
    )


@router.post("/reset-password", response_model=MessageResponse)
@limiter.limit("5/minute")
async def reset_password(request: Request, payload: ResetPasswordRequest, session: AsyncSession = Depends(get_session)) -> MessageResponse:
    user = (await session.exec(select(User).where(User.email == payload.email))).first()
    if user and user.is_active and not user.is_deleted:
        user.reset_password_token = token_urlsafe(32)
        user.reset_password_expires_at = datetime.now(UTC) + timedelta(hours=1)
        session.add(user)
        await session.commit()
        send_transactional_email_task.delay(  # pyright: ignore[reportFunctionMemberAccess]
            "reset",
            email=user.email,
            reset_token=user.reset_password_token,
            tenant_id=str(user.tenant_id),
        )
        await write_audit_log(
            session,
            tenant_id=user.tenant_id,
            actor_user_id=user.id,
            action="auth.reset_password_requested",
            entity_type="user",
            entity_id=str(user.id),
        )

    return MessageResponse(message="If the account exists, reset instructions were generated")


@router.post("/reset-password/confirm", response_model=MessageResponse)
async def confirm_reset_password(
    payload: ConfirmResetPasswordRequest,
    session: AsyncSession = Depends(get_session),
) -> MessageResponse:
    user = (await session.exec(select(User).where(User.reset_password_token == payload.token))).first()
    if not user or not user.reset_password_expires_at or user.reset_password_expires_at < datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    user.hashed_password = get_password_hash(payload.new_password)
    user.reset_password_token = None
    user.reset_password_expires_at = None
    user.refresh_token_version += 1
    session.add(user)
    await session.commit()
    return MessageResponse(message="Password updated")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(payload: VerifyEmailRequest, session: AsyncSession = Depends(get_session)) -> MessageResponse:
    user = (await session.exec(select(User).where(User.email_verification_token == payload.token))).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")

    user.email_verified = True
    user.email_verification_token = None
    session.add(user)
    await session.commit()
    return MessageResponse(message="Email verified")


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all_devices(payload: RefreshRequest, session: AsyncSession = Depends(get_session)) -> MessageResponse:
    try:
        token_data = decode_token(payload.refresh_token)
        user_id = UUID(token_data["sub"])
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.refresh_token_version += 1
    session.add(user)
    await session.commit()
    return MessageResponse(message="Logged out from all devices")
