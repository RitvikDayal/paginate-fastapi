import pytest
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from tests.models.user import User


@pytest.fixture(scope="module")
async def sample_users(session: AsyncSession):
    """Create sample data for testing."""

    users = [
        User(name="Alice Smith", email="alice@example.com", age=25),
        User(name="Bob Johnson", email="bob@example.com", age=30),
        User(name="Carol Williams", email="carol@example.com", age=35),
        User(name="David Brown", email="david@example.com", age=28),
        User(name="Eve Davis", email="eve@example.com", age=32),
    ]

    session.add_all(users)
    await session.commit()

    return users


@pytest.fixture(scope="module")
async def delete_users(session: AsyncSession):
    """Delete all users."""
    await session.execute(text("DELETE FROM users"))
    await session.commit()
