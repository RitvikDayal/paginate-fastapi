"""
FastAPI SQLModel Pagination Library

A library for adding pagination, filtering, and sorting capabilities
to FastAPI applications using SQLModel.

Example:
    from fastapi import FastAPI, Depends
    from pagination import PaginationMiddleware, PaginationParams

    app = FastAPI()
    paginator = PaginationMiddleware(get_session)

    @app.get("/items/")
    async def get_items(
        pagination: PaginationParams = Depends(),
        paginator: PaginationMiddleware = Depends(lambda: paginator),
    ):
        return await paginator.paginate(Item, pagination)
"""

from .middleware import PaginationMiddleware
from .models import FilterOperator, PageResponse, PaginationParams, SortOrder

__all__ = [
    "FilterOperator",
    "PageResponse",
    "PaginationMiddleware",
    "PaginationParams",
    "SortOrder",
]
