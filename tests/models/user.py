"""User model."""
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """User model."""

    __tablename__ = "users"
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str
    age: int
