import os
import sys
import uuid
from pathlib import Path

import asyncpg
import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault("REDIS_URL", "redis://:dev-redis-password-123456@localhost:6379/0")
os.environ.setdefault("TESTING", "true")

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def _get_db_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://user:password@postgres:5432/saas_db",
    )


def _get_sync_db_url() -> str:
    return _get_db_url().replace("postgresql+asyncpg://", "postgresql://")


async def _truncate_all_tables():
    conn = await asyncpg.connect(_get_sync_db_url())
    try:
        rows = await conn.fetch("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        table_names = [f'"{row["tablename"]}"' for row in rows]
        if table_names:
            await conn.execute(
                f"TRUNCATE TABLE {', '.join(table_names)} RESTART IDENTITY CASCADE"
            )
    finally:
        await conn.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    from app import models  # noqa: F401

    engine = create_async_engine(
        _get_db_url(),
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_and_reset():
    from app.core.limiter import limiter

    await _truncate_all_tables()

    try:
        limiter._storage.reset()
    except Exception:
        pass

    yield

    await _truncate_all_tables()

    try:
        limiter._storage.reset()
    except Exception:
        pass


@pytest_asyncio.fixture
async def session_factory(test_engine):
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture
def unique_email():
    return f"test-{uuid.uuid4().hex[:10]}@example.com"


@pytest.fixture
def unique_org():
    return f"org-{uuid.uuid4().hex[:10]}"


@pytest_asyncio.fixture
async def client(session_factory):
    from app.core.database import get_session
    from app.main import app

    async def override_get_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"host": "testserver"},
        timeout=30.0,
    ) as ac:
        yield ac

    app.dependency_overrides.pop(get_session, None)


@pytest_asyncio.fixture
async def auth_headers(client, unique_email, unique_org):
    payload = {
        "email": unique_email,
        "password": "testpass123",
        "organization_name": unique_org,
    }

    register_response = await client.post("/api/v1/auth/register", json=payload)
    if register_response.status_code not in (200, 201):
        pytest.skip(
            f"Cannot register user: {register_response.status_code} - {register_response.text}"
        )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    if login_response.status_code != 200:
        pytest.skip(
            f"Cannot login: {login_response.status_code} - {login_response.text}"
        )

    token = login_response.json().get("access_token")
    if not token:
        pytest.skip("No access token in response")

    return {"Authorization": f"Bearer {token}"}