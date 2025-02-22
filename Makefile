.PHONY: format lint test clean build publish install-dev setup-hooks

install-dev:
	poetry install --with dev

setup-hooks:
	poetry run pre-commit install

format:
	poetry run black pagination tests
	poetry run ruff --fix pagination tests

lint:
	poetry run black --check pagination tests
	poetry run ruff check pagination tests
	poetry run mypy pagination tests

test:
	poetry run pytest tests -v --cov=pagination --cov-report=term-missing

clean:
	rm -rf dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +

build: clean
	poetry build

publish: build
	poetry publish

pre-commit:
	poetry run pre-commit run --all-files
