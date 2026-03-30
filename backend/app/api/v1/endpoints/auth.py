from fastapi import APIRouter

from app.core.security import create_access_token, create_refresh_token
from app.schemas.auth import LoginRequest, RegisterRequest, Token

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest) -> Token:
    return Token(
        access_token=create_access_token(payload.email),
        refresh_token=create_refresh_token(payload.email),
    )


@router.post("/register")
async def register(payload: RegisterRequest) -> dict[str, str]:
    return {"message": f"registered {payload.email}"}


@router.post("/refresh")
async def refresh() -> dict[str, str]:
    return {"message": "refreshed"}


@router.post("/reset-password")
async def reset_password() -> dict[str, str]:
    return {"message": "reset sent"}


@router.post("/verify-email")
async def verify_email() -> dict[str, str]:
    return {"message": "verified"}
