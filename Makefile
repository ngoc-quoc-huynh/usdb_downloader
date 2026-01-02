.PHONY: check_style fix_style run run_in_docker test


_check_pyright:
	uv run pyright src/ tests/

_check_format:
	uv run ruff format src/ tests/

_check_lint:
	uv run ruff check src/ tests/

_fix_lint:
	uv run ruff check src/ tests/ --fix

check_style:
	$(MAKE) -j2 _check_pyright _check_format _check_lint

fix_style:
	$(MAKE) -j2 _check_pyright _check_format _fix_lint

run:
	uv run usdb-downloader

run_in_docker:
	docker compose run --rm usdb-downloader

test:
	uv run pytest -v --tb=long
