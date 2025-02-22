"""
Pagination middleware for FastAPI applications.

This module provides the core pagination functionality, including:
- Async session handling
- Query building with filters
- Sorting implementation
- Pagination calculation

The middleware can be used with any SQLModel-based FastAPI application
to add pagination, filtering, and sorting capabilities.
"""

from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager

from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlmodel import SQLModel, func, select

from .models import FilterOperator, PageResponse, PaginationParams, SortOrder


class PaginationMiddleware:
    """
    Middleware for handling pagination in FastAPI applications.

    This class provides methods to paginate SQLModel queries with
    support for filtering and sorting. It handles both async context
    managers and async generators for database sessions.

    Attributes:
        session_maker: Callable that provides database sessions
        default_page_size: Default number of items per page
    """

    def __init__(
        self,
        session_maker: Callable[[], AsyncSession | AsyncGenerator[AsyncSession, None]],
        default_page_size: int = 10,
    ):
        """
        Initialize the pagination middleware.

        Args:
            session_maker: Function that returns a database session
            default_page_size: Default number of items per page
        """
        self.session_maker = session_maker
        self.default_page_size = default_page_size

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session using the session maker.

        This method handles both async context managers and async generators,
        making it compatible with FastAPI dependency injection.

        Yields:
            AsyncSession: Database session
        """
        session_factory = self.session_maker()
        if hasattr(session_factory, "__aenter__"):
            async with session_factory as session:
                yield session
        else:
            try:
                session = await anext(session_factory)
                yield session
            finally:
                try:
                    await session_factory.aclose()
                except RuntimeError as ex:
                    if "already closed" not in str(ex):
                        raise ex

    def _apply_filter(
        self, query: Select, model: type[SQLModel], params: PaginationParams
    ) -> Select:
        """
        Apply filter conditions to the query.

        Args:
            query: Base SQLAlchemy select query
            model: SQLModel class to query
            params: Pagination parameters containing filter settings

        Returns:
            Select: Query with filters applied
        """
        if not all([params.filter_field, params.filter_operator, params.filter_value is not None]):
            return query

        field = getattr(model, params.filter_field)

        filter_map = {
            FilterOperator.EQ: lambda f, v: f == v,
            FilterOperator.NEQ: lambda f, v: f != v,
            FilterOperator.GT: lambda f, v: f > v,
            FilterOperator.LT: lambda f, v: f < v,
            FilterOperator.GTE: lambda f, v: f >= v,
            FilterOperator.LTE: lambda f, v: f <= v,
            FilterOperator.LIKE: lambda f, v: f.like(f"%{v}%"),
            FilterOperator.ILIKE: lambda f, v: f.ilike(f"%{v}%"),
            FilterOperator.IN: lambda f, v: f.in_(v),
            FilterOperator.NOT_IN: lambda f, v: ~f.in_(v),
        }

        filter_func = filter_map[params.filter_operator]
        return query.where(filter_func(field, params.filter_value))

    def _apply_sort(self, query: Select, model: type[SQLModel], params: PaginationParams) -> Select:
        """
        Apply sorting to the query.

        Args:
            query: Base SQLAlchemy select query
            model: SQLModel class to query
            params: Pagination parameters containing sort settings

        Returns:
            Select: Query with sorting applied
        """
        if not params.sort_by:
            return query

        field = getattr(model, params.sort_by)
        return query.order_by(desc(field) if params.sort_order == SortOrder.DESC else asc(field))

    async def paginate(
        self, model: type[SQLModel], params: PaginationParams | None = None
    ) -> PageResponse:
        """
        Paginate a SQLModel query with optional filtering and sorting.

        This method handles the complete pagination process:
        1. Builds the base query
        2. Applies any filters
        3. Applies sorting
        4. Calculates total count
        5. Applies pagination
        6. Returns formatted response

        Args:
            model: SQLModel class to paginate
            params: Pagination, filtering, and sorting parameters

        Returns:
            PageResponse: Paginated results with metadata
        """
        if params is None:
            params = PaginationParams(page_size=self.default_page_size)

        async with self.get_session() as session:
            # Build query
            query = select(model)
            query = self._apply_filter(query, model, params)
            query = self._apply_sort(query, model, params)

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total = (await session.execute(count_query)).scalar() or 0

            # Apply pagination
            query = query.offset(params.offset).limit(params.page_size)
            result = await session.execute(query)
            items = result.scalars().all()

            # Calculate pagination metadata
            pages = (total + params.page_size - 1) // params.page_size if total > 0 else 0

            return PageResponse(
                items=items,
                total=total,
                page=params.page,
                page_size=params.page_size,
                pages=pages,
                has_next=params.page < pages,
                has_previous=params.page > 1,
            )
