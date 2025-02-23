"""Test the pagination decorator."""

import httpx
import pytest
from fastapi import Depends, FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from pagination import FilterOperator, PageResponse, PaginationParams, paginate
from tests.fixtures import delete_users, paginator, sample_users  # noqa: F401
from tests.models.user import User


@pytest.fixture
async def app(session: AsyncSession):
    """Create a test FastAPI application."""
    app = FastAPI()

    async def get_db():
        yield session

    @app.get("/users/", response_model=PageResponse[User])
    @paginate(User, get_db)
    async def get_users(
        db: AsyncSession,
        pagination: PaginationParams,
    ):
        db = db if db else Depends(get_db)
        pagination = pagination if pagination else Depends()
        pass  # Decorator handles everything

    @app.get("/users/custom/")
    @paginate(User, get_db)
    async def get_users_custom(
        db: AsyncSession,
        pagination: PaginationParams,
    ):
        db = db if db else Depends(get_db)
        pagination = pagination if pagination else Depends()
        # Return both the pagination data and extra data
        stmt = select(User)
        result = await db.execute(stmt)
        users = result.scalars().all()  # Properly fetch users from database
        print(users)
        return {"extra_data": "test", "items": users}

    return app


@pytest.fixture
async def client(app: FastAPI):
    """Create a test client."""
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_basic_pagination(client: AsyncClient, sample_users):  # noqa: F811
    """Test basic pagination without any filters or sorting."""
    response = await client.get("/users/", params={"page": 1, "page_size": 2})
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["pages"] == 3
    assert data["has_next"] is True
    assert data["has_previous"] is False


@pytest.mark.asyncio
async def test_pagination_with_filtering(client: AsyncClient, sample_users):  # noqa: F811
    """Test pagination with filtering."""
    params = {
        "filter_field": "age",
        "filter_operator": FilterOperator.GT.value,
        "filter_value": "30",
        "page": 1,
        "page_size": 10,
    }
    response = await client.get("/users/", params=params)
    assert response.status_code == 200

    data = response.json()
    assert all(user["age"] > 30 for user in data["items"])


@pytest.mark.asyncio
async def test_pagination_with_sorting(client: AsyncClient, sample_users):  # noqa: F811
    """Test pagination with sorting."""
    params = {"sort_by": "age", "sort_order": "desc", "page": 1, "page_size": 10}
    response = await client.get("/users/", params=params)
    assert response.status_code == 200

    data = response.json()
    ages = [user["age"] for user in data["items"]]
    assert ages == sorted(ages, reverse=True)


@pytest.mark.asyncio
async def test_pagination_last_page(client: AsyncClient, sample_users):  # noqa: F811
    """Test pagination on the last page."""
    response = await client.get("/users/", params={"page": 3, "page_size": 2})
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 1  # Last page with remaining item
    assert data["has_next"] is False
    assert data["has_previous"] is True


@pytest.mark.asyncio
async def test_pagination_invalid_page(client: AsyncClient, sample_users):  # noqa: F811
    """Test pagination with invalid page number."""
    response = await client.get("/users/", params={"page": 99, "page_size": 10})
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 0
    assert data["has_next"] is False
    assert data["has_previous"] is True


@pytest.mark.asyncio
async def test_pagination_with_search(client: AsyncClient, sample_users):  # noqa: F811
    """Test pagination with search/contains filter."""
    params = {
        "filter_field": "age",
        "filter_operator": FilterOperator.GT.value,
        "filter_value": "30",
        "page": 1,
        "page_size": 10,
    }
    response = await client.get("/users/", params=params)
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) > 0  # First verify we have items
    assert all(user["age"] > 30 for user in data["items"])


@pytest.mark.asyncio
async def test_custom_return_data(client: AsyncClient, sample_users):  # noqa: F811
    """Test that the decorator preserves custom return data."""
    response = await client.get("/users/custom/")
    assert response.status_code == 200

    data = response.json()
    print(data)
    assert "items" in data  # Pagination data is present
    assert len(data["items"]) > 0


@pytest.mark.asyncio
async def test_pagination_empty_db(client: AsyncClient, delete_users):  # noqa: F811
    """Test pagination with empty database."""
    response = await client.get("/users/", params={"page": 1, "page_size": 10})
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 0
    assert data["total"] == 0
    assert data["pages"] == 0
    assert data["has_next"] is False
    assert data["has_previous"] is False
