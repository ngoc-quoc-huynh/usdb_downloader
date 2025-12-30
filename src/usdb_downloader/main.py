import argparse
import asyncio
import logging
from pathlib import Path
from typing import Final

from usdb_downloader import Parser, YoutubeDownloader

logger = logging.getLogger(__name__)

_INPUT_DIR: Final[Path] = Path("./songs/input")
_OUTPUT_DIR: Final[Path] = Path("./songs/output")


def _setup_logging(verbose: bool) -> None:
    if not verbose:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s - %(message)s",
        datefmt="%H:%M:%S",
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="USDB Downloader CLI")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args()


async def _run() -> None:
    logger.info("Starting application")

    parser = Parser(input_dir=_INPUT_DIR, output_dir=_OUTPUT_DIR)
    youtube_downloader = YoutubeDownloader()

    for file in parser.iter_files():
        parser.write_file(file)
        video_id = file.video_id
        output_path = _OUTPUT_DIR / file.name
        await asyncio.gather(
            youtube_downloader.download_audio(
                video_id=video_id,
                output_path=output_path,
            ),
            youtube_downloader.download_video(
                video_id=video_id,
                output_path=output_path,
            ),
        )

    logger.info("Finished application")


def main() -> None:
    args = _parse_args()
    _setup_logging(args.verbose)

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception:
        logger.exception("Application failed")
        raise


if __name__ == "__main__":
    main()
