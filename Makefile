.PHONY: style run

style:
	uv run pyright
	uv run ruff format src/

run:
	uv run usdb-downloader
