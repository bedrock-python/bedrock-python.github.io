.PHONY: install fmt docs-catalog docs-serve docs-serve-en docs-build docs-check clean

install:
	uv sync --group dev
	uv run pre-commit install --hook-type commit-msg

fmt:
	uv run pre-commit run --all-files

docs-catalog:
	uv run --no-dev --group docs python scripts/build_blog_catalog.py

docs-serve:
	uv run --no-dev --group docs python scripts/build_site.py --serve

docs-serve-en:
	uv run --no-dev --group docs python scripts/build_blog_catalog.py --language en
	uv run --no-dev --group docs zensical serve

docs-build:
	uv run --no-dev --group docs python scripts/build_site.py

docs-check:
	uv run --no-dev --group docs python -m unittest discover -s tests
	uv run --no-dev --group docs python scripts/build_blog_catalog.py --check

clean:
	python -c "import shutil, os; [shutil.rmtree(p, ignore_errors=True) for p in ['site', '.cache'] if os.path.exists(p)]"
