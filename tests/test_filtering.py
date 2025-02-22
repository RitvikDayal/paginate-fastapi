import pytest

from pagination import FilterOperator, PaginationParams
from tests.models.user import User


@pytest.mark.asyncio
async def test_filter_equals(paginator, sample_users):
    """Test filtering with equals operator."""
    params = PaginationParams(
        filter_field="age", filter_operator=FilterOperator.EQ, filter_value=30
    )
    result = await paginator.paginate(User, params)

    assert len(result.items) == 1
    assert result.items[0].age == 30


@pytest.mark.asyncio
async def test_filter_greater_than(paginator, sample_users):
    """Test filtering with greater than operator."""
    params = PaginationParams(
        filter_field="age", filter_operator=FilterOperator.GT, filter_value=30
    )
    result = await paginator.paginate(User, params)

    assert all(user.age > 30 for user in result.items)


@pytest.mark.asyncio
async def test_filter_like(paginator, sample_users):
    """Test filtering with LIKE operator."""
    params = PaginationParams(
        filter_field="name", filter_operator=FilterOperator.LIKE, filter_value="Brown"
    )
    result = await paginator.paginate(User, params)

    assert len(result.items) == 1
    assert result.items[0].name == "David Brown"
    assert result.items[0].email == "david@example.com"
    assert result.items[0].age == 28


@pytest.mark.asyncio
async def test_filter_in(paginator, sample_users):
    """Test filtering with IN operator."""
    params = PaginationParams(
        filter_field="age", filter_operator=FilterOperator.IN, filter_value=[25, 30]
    )
    result = await paginator.paginate(User, params)

    assert len(result.items) == 2
    assert all(user.age in [25, 30] for user in result.items)
