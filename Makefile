.PHONY: style run test


_pyright:
	uv run pyright

_ruff:
	uv run ruff format src/ tests/

style:
	$(MAKE) -j2 _pyright _ruff

run:
	uv run usdb-downloader

test:
	pytest
