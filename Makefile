.PHONY: install fmt docs-serve docs-build clean

install:
	uv sync --group dev
	uv run pre-commit install --hook-type commit-msg

fmt:
	uv run pre-commit run --all-files

docs-serve:
	uv run --no-dev --group docs zensical serve

docs-build:
	uv run --no-dev --group docs zensical build --clean

clean:
	python -c "import shutil, os; [shutil.rmtree(p, ignore_errors=True) for p in ['site', '.cache'] if os.path.exists(p)]"
