# My Project Repository Guidelines

## Package Management

### Using `uv` for Dependency Management

This project uses `uv` for dependency management instead of pip. Always use `uv` for installing packages:

```bash
# For application dependencies
uv add package_name

# For development dependencies
uv add --group dev package_name
```

### Adding Dependencies

When adding new dependencies:

1. Always update the `pyproject.toml` file
2. Use specific version constraints when appropriate
3. Document why the dependency is needed with a comment

### Current Dependencies

#### Application Dependencies
- fastapi: Web framework
- uvicorn: ASGI server
- pydantic: Data validation
- httpx: Async HTTP client
- redis-om: Redis object mapping (with async support)
- dspy-ai: AI response generation

#### Development Dependencies
- pytest: Testing framework
- pytest-asyncio: For testing async functions
- black: Code formatting
- isort: Import sorting
- mypy: Type checking
- ruff: Modern Python linter
- flake8: Linting

## Project Structure

- `app/`: Main application code
  - `models/`: Pydantic models
  - `services/`: Business logic services
  - `routers/`: API endpoints
- `tests/`: Test files
- `run.py`: Application entry point

## Testing

- Use pytest for all tests
- Use pytest-asyncio for testing async functions
- Mock external dependencies in tests

## Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Use mypy for type checking