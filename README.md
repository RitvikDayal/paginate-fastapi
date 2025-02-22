# Paginate FastAPI

[![PyPI version](https://badge.fury.io/py/paginate-fastapi.svg)](https://badge.fury.io/py/paginate-fastapi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A simple and efficient pagination library for FastAPI applications.

## Features

- Easy-to-use pagination with FastAPI
- Async support out of the box
- Flexible filtering options
- Customizable sorting
- Type-safe with full type hints
- Compatible with FastAPI

## Installation

### Using Poetry
```bash
poetry add paginate-fastapi
```

### Using Pip
```bash
pip install paginate-fastapi
```

## Quick Start

```python
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Field
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from pagination import PaginationMiddleware, PaginationParams

app = FastAPI()

# Initialize your database
engine = create_async_engine("sqlite+aiosqlite:///database.db")

async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session

paginator = PaginationMiddleware(get_session)

# Define your model
class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    email: str
    age: int

# Add pagination to your endpoint
@app.get("/users/")
async def get_users(
    pagination: PaginationParams = Depends(),
    paginator: PaginationMiddleware = Depends(lambda: paginator),
):
    return await paginator.paginate(User, pagination)
```

### Sample Request and Response

```bash
curl -X GET "http://localhost:8000/users/?page=1&page_size=10"
```

```json
{
    "items": [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "age": 30
        }
    ],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "pages": 10,
    "has_next": true,
    "has_previous": false
}
```

### Sorting

```bash
# Sort by name ascending
users/?sort_by=name&sort_order=asc

# Sort by age descending
users/?sort_by=age&sort_order=desc
```

### Filtering

```bash
# Filter users by age greater than 30
users/?filter_field=age&filter_operator=gt&filter_value=30

# Filter users by name containing "John"
users/?filter_field=name&filter_operator=like&filter_value=John

# Filter users by age in a list
users/?filter_field=age&filter_operator=in&filter_value=[25,30,35]
```

### Available Filter Operators

- `eq`: Equal to
- `ne`: Not equal to
- `gt`: Greater than
- `lt`: Less than
- `ge`: Greater than or equal to
- `le`: Less than or equal to
- `like`: Contains (case-sensitive)
- `ilike`: Contains (case-insensitive)
- `in`: In list of values
- `not_in`: Not in list of values

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/ritvikdayal/paginate-fastapi.git
cd paginate-fastapi

# Install dependencies
poetry install
```

### Running Tests

```bash
poetry run pytest
```

### Code Quality

```bash
# Format code
poetry run black .

# Run linter
poetry run ruff .

# Type checking
poetry run mypy .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

