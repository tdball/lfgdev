format:
    uv run ruff format
    uv run ruff check --select I --fix

test:
    uv run ruff format --check
    uv run ruff check --select I
    uv run mypy
    uv run pytest -sv

profile:
    uv run pytest -m profiling
