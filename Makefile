.PHONY: style run test run_in_docker


_pyright:
	uv run pyright

_ruff:
	uv run ruff format src/ tests/

style:
	$(MAKE) -j2 _pyright _ruff

run:
	uv run usdb-downloader

run_in_docker:
	docker compose run --rm usdb-downloader

test:
	pytest
