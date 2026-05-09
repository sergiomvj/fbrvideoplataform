from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)


def get_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url)


def get_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_db(database_url: str) -> None:
    global _session_factory
    engine = get_engine(database_url)
    _session_factory = get_session_factory(engine)


async def async_session() -> AsyncGenerator[AsyncSession, None]:
    if _session_factory is None:
        from infrastructure.settings.config import Settings

        init_db(Settings().DATABASE_URL)
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
