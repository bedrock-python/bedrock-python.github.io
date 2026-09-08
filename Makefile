.PHONY: install fmt docs-catalog docs-serve docs-build clean

install:
	uv sync --group dev
	uv run pre-commit install --hook-type commit-msg

fmt:
	uv run pre-commit run --all-files

docs-catalog:
	uv run --no-dev --group docs python scripts/build_blog_catalog.py

docs-serve: docs-catalog
	uv run --no-dev --group docs zensical serve

docs-build: docs-catalog
	uv run --no-dev --group docs zensical build --clean

clean:
	python -c "import shutil, os; [shutil.rmtree(p, ignore_errors=True) for p in ['site', '.cache'] if os.path.exists(p)]"
