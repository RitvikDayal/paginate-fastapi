import pytest

from pagination import FilterOperator, PaginationParams, SortOrder
from tests.fixtures import paginator, sample_users  # noqa: F401
from tests.models.user import User


@pytest.mark.asyncio()
async def test_sort_ascending(paginator, sample_users):  # noqa: F811
    """Test sorting in ascending order."""
    params = PaginationParams(sort_by="age", sort_order=SortOrder.ASC)
    result = await paginator.paginate(User, params)

    ages = [user.age for user in result.items]
    assert ages == sorted(ages)


@pytest.mark.asyncio
async def test_sort_descending(paginator, sample_users):  # noqa: F811
    """Test sorting in descending order."""
    params = PaginationParams(sort_by="name", sort_order=SortOrder.DESC)
    result = await paginator.paginate(User, params)

    names = [user.name for user in result.items]
    assert names == sorted(names, reverse=True)


@pytest.mark.asyncio
async def test_sort_and_filter(paginator, sample_users):  # noqa: F811
    """Test combining sorting and filtering."""
    params = PaginationParams(
        sort_by="name",
        sort_order=SortOrder.ASC,
        filter_field="age",
        filter_operator=FilterOperator.GT,
        filter_value=30,
    )
    result = await paginator.paginate(User, params)

    assert all(user.age > 30 for user in result.items)
    names = [user.name for user in result.items]
    assert names == sorted(names)


@pytest.mark.asyncio
async def test_sort_with_pagination(paginator, sample_users):  # noqa: F811
    """Test sorting with pagination."""
    params = PaginationParams(page=1, page_size=2, sort_by="age", sort_order=SortOrder.ASC)
    result = await paginator.paginate(User, params)

    assert len(result.items) == 2
    ages = [user.age for user in result.items]
    assert ages == sorted(ages)
    assert result.has_next is True
