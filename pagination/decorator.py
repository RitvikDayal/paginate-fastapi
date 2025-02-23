"""
Pagination utilities.
"""

from collections.abc import Callable

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

from pagination.models import PageResponse, PaginationParams


def paginate(model: type[SQLModel], db_dependency: Callable):
    """
    Decorator for FastAPI endpoints to add pagination support.

    Usage:
    @router.get("/", response_model=PageResponse[YourModel])
    @paginate(YourModel, lambda: get_db)
    async def get_items(
        db: AsyncSession = Depends(get_db),
        pagination: PaginationParams = Depends()
    ):
        pass  # The decorator handles everything
    """

    def decorator(function: Callable) -> Callable:
        def _apply_filter(query, field, operator: str, value):
            """Apply filter operation to query."""
            filter_ops = {
                "eq": lambda: field == value,
                "neq": lambda: field != value,
                "gt": lambda: field > value,
                "lt": lambda: field < value,
                "gte": lambda: field >= value,
                "lte": lambda: field <= value,
                "in": lambda: field.in_(value),
                "not_in": lambda: field.not_in(value),
                "contains": lambda: field.contains(value),
            }
            if op_func := filter_ops.get(operator):
                return query.where(op_func())
            return query

        async def wrapper(
            db: AsyncSession = Depends(db_dependency),  # noqa: B008
            pagination: PaginationParams = Depends(),  # noqa: B008
        ) -> PageResponse:
            # Build the base query
            query = select(model)

            # Apply filtering if specified
            if all(
                [
                    pagination.filter_field,
                    pagination.filter_operator,
                    pagination.filter_value,
                ]
            ):
                if field := getattr(model, pagination.filter_field, None):
                    query = _apply_filter(
                        query, field, pagination.filter_operator, pagination.filter_value
                    )

            # Apply sorting if specified
            if pagination.sort_by:
                field = getattr(model, pagination.sort_by, None)
                if field is not None:
                    query = query.order_by(
                        field.desc() if pagination.sort_order == "desc" else field
                    )

            # Execute count query
            count_query = select(func.count()).select_from(query.subquery())
            total = await db.scalar(count_query) or 0

            # Calculate pages
            pages = (total + pagination.page_size - 1) // pagination.page_size

            # Apply pagination
            offset = (pagination.page - 1) * pagination.page_size
            query = query.offset(offset).limit(pagination.page_size)

            # Execute main query
            result = await db.execute(query)
            items = result.scalars().all()

            # Calculate pagination flags
            has_next = pagination.page < pages
            has_previous = pagination.page > 1

            # Create base pagination response
            pagination_response = {
                "items": items,
                "total": total,
                "page": pagination.page,
                "pages": pages,
                "page_size": pagination.page_size,
                "has_next": has_next,
                "has_previous": has_previous,
            }

            # Execute the original function to get any custom data
            custom_data = await function(db=db, pagination=pagination)
            print(custom_data)
            if isinstance(custom_data, dict):
                # Merge custom data with pagination data
                pagination_response.update(custom_data)
            print(pagination_response)

            return pagination_response

        return wrapper

    return decorator
