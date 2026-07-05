"""Async session factory (SQLAlchemy 2.x async engine).

Scaffolding for persistence. The mock chat path never opens a session, so the
gateway answers with zero DB dependency (see TASK constraint / plan RK-5).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from _common.env import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    """Create (once) the async engine from settings.database_url."""
    settings = get_settings()
    return create_async_engine(settings.database_url, future=True)


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Return a cached async session factory."""
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a scoped async session."""
    factory = get_sessionmaker()
    async with factory() as session:
        yield session
