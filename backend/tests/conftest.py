import asyncio

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.pool import StaticPool

from infrastructure.db.models import Base
from infrastructure.db.session import async_session
from main import app

TEST_INTERNAL_TOKEN = "test-internal-token-12345"


def _create_test_engine():
    return create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _init_test_db(engine):
    async def _setup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_setup())


def _dispose_engine(engine):
    asyncio.run(engine.dispose())


@pytest.fixture
def client():
    engine = _create_test_engine()
    _init_test_db(engine)

    test_session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_async_session():
        async with test_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[async_session] = override_async_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    _dispose_engine(engine)


@pytest.fixture
def db_session_factory():
    engine = _create_test_engine()
    _init_test_db(engine)

    test_session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_async_session():
        async with test_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[async_session] = override_async_session

    yield test_session_factory

    app.dependency_overrides.clear()
    _dispose_engine(engine)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {
        "X-User-Id": "test-user-001",
        "X-Organization-Id": "default",
        "X-Internal-Token": TEST_INTERNAL_TOKEN,
    }


@pytest.fixture(autouse=True)
def set_internal_token(monkeypatch):
    monkeypatch.setenv("BACKEND_INTERNAL_TOKEN", TEST_INTERNAL_TOKEN)
