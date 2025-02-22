import pytest

from pagination import PaginationParams
from tests.models.user import User


@pytest.mark.asyncio
async def test_basic_pagination(paginator, sample_users):
    """Test basic pagination without filters or sorting."""
    params = PaginationParams(page=1, page_size=2)
    result = await paginator.paginate(User, params)

    assert len(result.items) == 2
    assert result.total == 5
    assert result.page == 1
    assert result.page_size == 2
    assert result.pages == 3
    assert result.has_next is True
    assert result.has_previous is False


@pytest.mark.asyncio
async def test_pagination_last_page(paginator, sample_users):
    """Test pagination on the last page."""
    params = PaginationParams(page=3, page_size=2)
    result = await paginator.paginate(User, params)

    assert len(result.items) == 1
    assert result.total == 5
    assert result.page == 3
    assert result.has_next is False
    assert result.has_previous is True


@pytest.mark.asyncio
async def test_pagination_invalid_page(paginator, sample_users):
    """Test pagination with invalid page number."""
    params = PaginationParams(page=99, page_size=10)
    result = await paginator.paginate(User, params)

    assert len(result.items) == 0
    assert result.total == 5
    assert result.has_next is False
    assert result.has_previous is True


@pytest.mark.asyncio
async def test_pagination_empty_result(paginator, delete_users):
    """Test pagination with no data."""
    params = PaginationParams(page=1, page_size=10)
    result = await paginator.paginate(User, params)

    assert len(result.items) == 0
    assert result.total == 0
    assert result.pages == 0
    assert result.has_next is False
    assert result.has_previous is False
