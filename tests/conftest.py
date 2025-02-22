from typing import AsyncGenerator
import pytest
from sqlmodel.pool import StaticPool
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

@pytest.fixture(scope="module")
async def engine():
    """Create a test engine with in-memory SQLite database."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="module")
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test session."""
    async with AsyncSession(engine) as session:
        yield session
