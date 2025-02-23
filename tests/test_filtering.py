import pytest

from pagination import FilterOperator, PaginationParams
from tests.fixtures import paginator, sample_users  # noqa: F401
from tests.models.user import User


@pytest.mark.asyncio
async def test_filter_equals(paginator, sample_users):  # noqa: F811
    """Test filtering with equals operator."""
    params = PaginationParams(
        filter_field="age", filter_operator=FilterOperator.EQ, filter_value=30
    )
    result = await paginator.paginate(User, params)

    assert len(result.items) == 1
    assert result.items[0].age == 30


@pytest.mark.asyncio
async def test_filter_greater_than(paginator, sample_users):  # noqa: F811
    """Test filtering with greater than operator."""
    params = PaginationParams(
        filter_field="age", filter_operator=FilterOperator.GT, filter_value=30
    )
    result = await paginator.paginate(User, params)

    assert all(user.age > 30 for user in result.items)
