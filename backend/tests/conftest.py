import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.core.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    import asyncio

    async def _init() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.create_all)

    async def _drop() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.drop_all)

    asyncio.run(_init())
    yield
    asyncio.run(_drop())


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
