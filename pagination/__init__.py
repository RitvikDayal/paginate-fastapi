"""
FastAPI SQLModel Pagination Library

A library for adding pagination, filtering, and sorting capabilities
to FastAPI applications using SQLModel.

Example:
    from fastapi import FastAPI, Depends
    from pagination import PaginationMiddleware, PaginationParams, paginate

    app = FastAPI()

    # Using middleware
    paginator = PaginationMiddleware(get_session)

    @app.get("/items/")
    async def get_items(
        pagination: PaginationParams = Depends(),
        paginator: PaginationMiddleware = Depends(lambda: paginator),
    ):
        return await paginator.paginate(Item, pagination)

    # Using decorator
    @app.get("/users/")
    @paginate(User, get_session)
    async def get_users():
        return {"extra": "Additional data can be included"}
"""

from .decorator import paginate
from .middleware import PaginationMiddleware
from .models import FilterOperator, PageResponse, PaginationParams, SortOrder

__all__ = [
    "FilterOperator",
    "PageResponse",
    "PaginationMiddleware",
    "PaginationParams",
    "SortOrder",
    "paginate",
]
