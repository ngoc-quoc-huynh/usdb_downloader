.PHONY: style run

style:
	uv run pyright
	uv run ruff format src/ tests/

run:
	uv run usdb-downloader
