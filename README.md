# usdb_downloader

[![build](https://github.com/ngoc-quoc-huynh/usdb_downloader/actions/workflows/usdb_downloader.yml/badge.svg?branch=main)](https://github.com/ngoc-quoc-huynh/usdb_downloader/actions/workflows/usdb_downloader.yml?query=branch%3Amain)
[![renovate enabled](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com/)
[![release](https://img.shields.io/github/v/release/ngoc-quoc-huynh/usdb_downloader)](https://github.com/ngoc-quoc-huynh/usdb_downloader/releases/latest)
[![license](https://img.shields.io/github/license/ngoc-quoc-huynh/usdb_downloader?branch=main)](https://raw.githubusercontent.com/ngoc-quoc-huynh/usdb_downloader/refs/heads/main/LICENSE)

A command-line tool for downloading and managing UltraStar Deluxe song files
from [USDB (UltraStar Deluxe Database)](https://usdb.animux.de/).

The tool takes `.txt` song files from USDB as input, automatically downloads the
corresponding audio and video files from YouTube, groups all related assets into a single
song folder, and searches for a cover in your browser.

<p align="center">
    <img
    src="https://github.com/user-attachments/assets/e8ba9d73-53ac-465d-b585-f91a326d297e"
    alt="Demo GIF"
    width="500"
  />
<p/>

## Prequisites

### asdf

We are using [asdf](https://asdf-vm.com/) to manage the dependencies. Make sure you have it
installed and then run the following command to install the required versions:

```bash
asdf install
```

If you don't have asdf installed or prefer not to use it, you can install the required tools manually instead:

- [python](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

Make sure to use the version specified in the [.tool-versions ](../.tool-versions) file to avoid compatibility issues.

## Local Development

### Install Dependencies

Install all project dependencies by running:

```bash
uv sync
```

### Configuration

The application is configured via environment variables. You can define them in a `.envrc` file located in the project
root.

> **Important:** The input directory is mandatory and must contain the `.txt` files to be processed.
> The output directory does not need to exist, it will be created automatically if missing.

| Variable     | Description                                                  | Default          |
|--------------|--------------------------------------------------------------|------------------|
| `INPUT_DIR`  | Directory containing input files                             | `./songs/input`  |
| `OUTPUT_DIR` | Directory containing parsed songs with audio and video files | `./songs/output` |

Make sure the input directory exists and place your `.txt` files there before running the application.

### Running the Application

Run the application locally with:

```bash
make run
```

### Running with Docker

If you prefer to run the application in a Docker container, use:

```bash
make run_in_docker
```

## Code Style

In our project, we follow a consistent code style to ensure readability, maintainability, and
collaboration among team members. Adhering to a unified code style not only improves code quality
but also enhances the overall development process.

We are using one tool to enforce code quality and consistency:

- [Ruff](https://docs.astral.sh/ruff/): A fast Python linter and formatter that replaces tools like `flake8`, `isort`,
  and more.
- [Pyright](https://microsoft.github.io/pyright/): A static type checker for Python that helps catch type-related issues
  early.

These tools are configured to work together to ensure a consistent code style. You can run them locally with:

```shell
make check_style
```

This command runs all configured linters and type checks and reports any issues found.

```shell
make fix_style
```

This command automatically formats the code and fixes issues where possible.

### Git Hooks

We use Git hooks to enforce code style and quality checks before committing changes. To set up Git hooks, run:

```shell
lefthook install
```

This command installs the necessary Git hooks in your local repository.
