format:
    uv run ruff format
    uv run ruff check --fix

test:
    uv run ruff check
    uv run ruff format --check
    uv run mypy
    uv run pytest -sv

profile:
    uv run pytest -m profiling
