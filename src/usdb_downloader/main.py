import argparse
import asyncio
import logging
import os
from importlib.metadata import version
from pathlib import Path
from typing import Final

from rich.logging import RichHandler

from usdb_downloader.app import App
from usdb_downloader.console import Console

logger = logging.getLogger(__name__)

_INPUT_DIR: Final[Path] = Path(os.getenv("INPUT_DIR", "./songs/input"))
_OUTPUT_DIR: Final[Path] = Path(os.getenv("OUTPUT_DIR", "./songs/output"))
_app_version: Final[str] = version("usdb-downloader")


def _setup_logging(verbose: bool) -> None:
    if verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler()],
        )
    else:
        logging.disable(logging.CRITICAL)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="USDB Downloader CLI")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_app_version}",
        help="Show version information",
    )

    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    _setup_logging(args.verbose)
    console = Console(not args.verbose)

    try:
        console.print_header(
            input_dir=_INPUT_DIR,
            output_dir=_OUTPUT_DIR,
            app_version=_app_version,
        )
        asyncio.run(
            App(
                input_dir=_INPUT_DIR,
                output_dir=_OUTPUT_DIR,
                console=console,
            ).run()
        )
    except KeyboardInterrupt:
        console.print_interrupt()
        logger.info("Interrupted by user")
    except Exception as e:
        console.print_failure(f"Application failed: {e}")
        logger.exception("Application failed")
        raise


if __name__ == "__main__":
    main()
