# Agent Instructions

## Project shape

- This is a Python command-line tool. Keep changes compatible with the Python minimum declared in `pyproject.toml`.
- Preserve the existing responsibilities: `Parser` reads and writes song files, `App` coordinates processing, `YoutubeDownloader` wraps yt-dlp, and `Console` handles Rich output.
- Inspect relevant source, tests, `pyproject.toml`, and `CONTRIBUTING.md` before changing behavior.

## Implementation

- Keep solutions small, readable, efficient, secure, and consistent with the project.
- Existing conventions are a starting point. Improve affected code consistently when justified, and report material changes.
- Avoid speculative abstractions, unrelated refactoring, and premature optimization.
- Carry out clear requests without unnecessary questions. Ask when ambiguity materially affects scope, safety, or design.
- Preserve CLI behavior and song-file compatibility. Ask before changing public contracts, adding dependencies, or raising Python or platform minimums.
- Treat song file contents, filenames, and video IDs as untrusted input. Validate or constrain values before using them in paths or URLs; keep writes within the configured output directory.
- Pass untrusted values as literal data to yt-dlp templates, logs, and Rich output. Do not let metadata become format directives or Rich markup.
- Keep filesystem, network, and download resource use bounded. Run blocking yt-dlp work off the asyncio event loop.
- Keep secrets out of source, logs, and Git.

## Tests and checks

- Add or update focused tests when behavior changes. Tests should use temporary directories and mock network and yt-dlp interactions.
- Run the relevant configured checks and report their actual results. Do not weaken tests or safeguards to make a check pass.
- Use these read-only checks:

  ```sh
  uv run ruff format src/ tests/ --check
  uv run ruff check src/ tests/
  uv run pyright src/ tests/
  uv run pytest -v --tb=long
  ```

- `make check_style` currently runs `ruff format` without `--check`, so it can modify files. Use the direct commands above for reviews.
- Tests mock external downloads. Report separately whether real YouTube, ffmpeg, or Docker behavior was exercised; mocked tests do not verify those integrations.

## Changes and Git

- Keep changes focused and preserve unrelated work. Reviews and diagnoses are read-only unless changes are requested.
- Do not create scratch files or directories. If one is unavoidable, ask first and remove it when finished.
- Ask before destructive actions unless the exact target and scope were already authorized. Commit, push, publish, or deploy only when explicitly requested.
- Follow the commit-message guidance in [CONTRIBUTING.md](CONTRIBUTING.md#commit-messages).
