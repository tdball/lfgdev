format:
    uv run ruff format
    uv run ruff check --fix
    uv run ruff check --select I --fix

test:
    uv run ruff check
    uv run ruff format --check
    uv run ty check
    uv run pytest --memray -sv

profile:
    uv run pytest --memray -m profiling


serve:
    uv run lfgdev-server -v
