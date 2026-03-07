# AGENTS.md - Development Guidelines for Agentic Coding

This document provides guidelines for agentic coding agents operating in this repository.

## Project Overview

- **Project Name**: playground
- **Language**: Python 3.12
- **Package Manager**: uv
- **Web Framework**: FastAPI
- **Testing Framework**: pytest
- **Linter**: ruff
- **Type Checker**: mypy

## Build / Lint / Test Commands

### Setup

```bash
uv sync
```

### Running the Application

```bash
uv run uvicorn playground:app --reload
```

### Running Tests

Run all tests:
```bash
uv run pytest tests
```

Run a single test file:
```bash
uv run pytest tests/test_example.py
```

Run a single test function:
```bash
uv run pytest tests/test_example.py::test_function_name
```

Run tests with verbose output:
```bash
uv run pytest -v tests
```

Run tests matching a pattern:
```bash
uv run pytest -k "test_pattern"
```

### Linting & Type Checking

Run ruff linter:
```bash
uv run ruff check .
```

Run ruff with auto-fix:
```bash
uv run ruff check --fix .
```

Run mypy type checker:
```bash
uv run mypy .
```

Run ruff formatter (format code):
```bash
uv run ruff format .
```

### Docker

Start local development environment:
```bash
docker-compose up -d
```

## Code Style Guidelines

### General Principles

- Follow PEP 8 style guide for Python code
- Use type hints for all function signatures and variables
- Keep functions small and focused (single responsibility)
- Write docstrings for all public functions and classes
- Tests file structure should be same to the source code for easy location the test and target.

### Formatting

- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use ruff formatter for automatic formatting:
  ```bash
  uv run ruff format .
  ```
- Add trailing commas in multi-line constructs

### Imports

- Use absolute imports (e.g., `from playground import utils`)
- Group imports in the following order:
  1. Standard library
  2. Third-party libraries
  3. Local application imports
- Use `__init__.py` for package exports
- Avoid wildcard imports (`from module import *`)

Example:
```python
# Standard library
import asyncio
from pathlib import Path
from typing import Optional

# Third-party
import fastapi
from fastapi import UploadFile

# Local
from playground import config
from playground.utils import helper_function
```

### Naming Conventions

- **Variables/functions**: snake_case (e.g., `calculate_total`, `file_path`)
- **Classes**: PascalCase (e.g., `EvaluationJob`, `ResultStore`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_CONCURRENT`, `DEFAULT_TIMEOUT`)
- **Private methods/variables**: prefix with underscore (e.g., `_internal_method`)
- **Type aliases**: suffix with `_type` (e.g., `ResultDictType`)

### Type Hints

- Always use type hints for function arguments and return values
- Use `Optional[X]` instead of `X | None`
- Use `list[T]`, `dict[K, V]` instead of `List[T]`, `Dict[K, V]`
- Use `None` instead of `type(None)`

Example:
```python
def process_file(file_path: Path, timeout: Optional[int] = None) -> dict[str, Any]:
    """Process a file and return results."""
    ...
```

### Error Handling

- Use specific exception types, avoid bare `except:`
- Use `try/except` only when necessary, prefer EAFP (Easier to Ask Forgiveness than Permission)
- Propagate exceptions with context using `raise ... from original_exception`
- Log errors with appropriate level before re-raising

Example:
```python
try:
    result = await client.get_object(bucket, key)
except ClientError as e:
    logger.error(f"Failed to get object: {key}, error: {e}")
    raise StorageError(f"Could not retrieve {key}") from e
```

### Async Code

- Use `async def` for functions that perform I/O operations
- Use `await` for all async calls
- Avoid blocking calls in async functions (use `asyncio.to_thread` if needed)
- Use `asyncio.gather` for concurrent operations

### Testing

- Place tests in the `tests/` directory
- Name test files as `test_<module_name>.py`
- Name test functions with `test_<description>` prefix
- Use pytest fixtures for setup/teardown
- Keep tests focused and independent
- Use descriptive assertion messages

Example:
```python
def test_evaluate_returns_result_url(setup_client):
    """Test that evaluate endpoint returns a signed result URL."""
    response = setup_client.post("/evaluate", json={
        "model_name": "test-model",
        "concurrent": 1,
        "signed_url": "https://example.com/file.csv"
    })
    assert response.status_code == 200
    assert "result_url" in response.json()
```

### Logging

- Use the `logging` module with `__name__` logger
- Use appropriate log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Include context in log messages

Example:
```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Starting evaluation for model: {model_name}")
logger.error(f"Evaluation failed: {error}", exc_info=True)
```

### Documentation

- Use Google-style docstrings
- Include Args, Returns, Raises sections for functions
- Document exceptions that may be raised
- Keep docstrings updated when changing code

Example:
```python
def upload_file(file: UploadFile, bucket: str) -> str:
    """Upload a file to S3 storage.

    Args:
        file: The file to upload.
        bucket: The target S3 bucket name.

    Returns:
        The signed URL for accessing the uploaded file.

    Raises:
        StorageError: If the upload fails.
    """
```

### Git Conventions

- Use meaningful commit messages
- Keep commits atomic and focused
- Create feature branches for new features
- Run lint and type checks before committing

## Project Structure

```
playground-poc/
├── playground/           # Main application code
│   ├── __init__.py
│   ├── app.py           # FastAPI application
│   ├── config.py        # Configuration
│   ├── constants.py     # Constants
│   ├── utils.py         # Utility functions
│   └── clients/         # Client modules
├── tests/               # Test suite
├── docs/                # Documentation
├── pyproject.toml       # Project configuration
└── README.md            # Project README
```

## Additional Resources

- FastAPI: https://fastapi.tiangolo.com/
- Ruff: https://docs.astral.sh/ruff/
- Mypy: https://mypy.readthedocs.io/
- pytest: https://docs.pytest.org/
