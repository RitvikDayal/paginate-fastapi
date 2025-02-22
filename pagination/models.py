"""
Models for the pagination library.

This module contains the core data models used for pagination, filtering, and sorting.
It defines the parameters that can be used to control pagination behavior and the
structure of pagination responses.
"""

from enum import Enum
from typing import Generic, TypeVar, Sequence, Optional, Any
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

class SortOrder(str, Enum):
    """
    Enumeration for sort order direction.
    
    Attributes:
        ASC: Ascending order (A to Z, 1 to 9)
        DESC: Descending order (Z to A, 9 to 1)
    """
    ASC = "asc"
    DESC = "desc"

class FilterOperator(str, Enum):
    """
    Enumeration for filter operations.
    
    Attributes:
        EQ: Equals (=)
        NEQ: Not equals (!=)
        GT: Greater than (>)
        LT: Less than (<)
        GTE: Greater than or equal (>=)
        LTE: Less than or equal (<=)
        LIKE: SQL LIKE pattern matching
        ILIKE: Case-insensitive LIKE pattern matching
        IN: Value in list
        NOT_IN: Value not in list
    """
    EQ = "eq"  # equals
    NEQ = "neq"  # not equals
    GT = "gt"  # greater than
    LT = "lt"  # less than
    GTE = "gte"  # greater than or equal
    LTE = "lte"  # less than or equal
    LIKE = "like"  # LIKE operator
    ILIKE = "ilike"  # ILIKE operator
    IN = "in"  # IN operator
    NOT_IN = "not_in"  # NOT IN operator

class PaginationParams(BaseModel):
    """
    Parameters for pagination, filtering, and sorting.
    
    This model can be used directly as a FastAPI dependency to receive
    pagination parameters from query strings.
    
    Attributes:
        page: Current page number (1-based)
        page_size: Number of items per page
        sort_by: Field name to sort by
        sort_order: Sort direction (asc/desc)
        filter_field: Field name to filter on
        filter_operator: Filter operation to apply
        filter_value: Value to filter by
    """
    page: int = Field(default=1, gt=0)
    page_size: int = Field(default=10, gt=0)
    sort_by: Optional[str] = None
    sort_order: SortOrder = SortOrder.ASC
    filter_field: Optional[str] = None
    filter_operator: Optional[FilterOperator] = None
    filter_value: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)

    @property
    def offset(self) -> int:
        """
        Calculate the SQL offset for the current page.
        
        Returns:
            int: Number of items to skip
        """
        return (self.page - 1) * self.page_size

class PageResponse(BaseModel, Generic[T]):
    """
    Generic response model for paginated results.
    
    Type parameter T represents the model type being paginated.
    
    Attributes:
        items: Sequence of items for the current page
        total: Total number of items across all pages
        page: Current page number
        page_size: Number of items per page
        pages: Total number of pages
        has_next: Whether there is a next page
        has_previous: Whether there is a previous page
    """
    items: Sequence[T]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_previous: bool
    
    model_config = ConfigDict(from_attributes=True)

