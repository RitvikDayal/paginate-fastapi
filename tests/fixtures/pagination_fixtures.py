import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from pagination.middleware import PaginationMiddleware


@pytest.fixture(scope="module")
def paginator(session: AsyncSession):
    """Create a paginator instance."""
    return PaginationMiddleware(lambda: session)
