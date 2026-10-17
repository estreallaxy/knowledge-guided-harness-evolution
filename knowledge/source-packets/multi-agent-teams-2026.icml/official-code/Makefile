.PHONY: test lint check format

# Run everything
check: test lint

# Run all tests
test:
	pytest

# Run linting and type checking
lint:
	ruff check .
	pyright

# Format code (fixes style issues)
format:
	ruff format .


