import argparse
import asyncio
import logging
from pathlib import Path
from typing import Final

from rich.logging import RichHandler
from usdb_downloader import Parser, YoutubeDownloader, Console
from usdb_downloader.youtube_downloader import YoutubeDownloaderException

logger = logging.getLogger(__name__)

_INPUT_DIR: Final[Path] = Path("./songs/input")
_OUTPUT_DIR: Final[Path] = Path("./songs/output")


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
        "-q",
        "--quiet",
        action="store_true",
        help="Disable console output",
    )
    return parser.parse_args()


async def _run(console: Console) -> None:
    logger.info("Starting application")

    parser = Parser(input_dir=_INPUT_DIR, output_dir=_OUTPUT_DIR)
    youtube_downloader = YoutubeDownloader()

    files = list(parser.iter_files())

    console.print_song_count(len(files))
    if not files:
        return

    processed = 0
    failed = 0

    for idx, file in enumerate(files, 1):
        console.print_song_start(idx=idx, total=len(files), name=file.name)

        try:
            parser.write_file(file)
            console.print_song_step("Parsed song file")

            video_id = file.video_id
            output_path = _OUTPUT_DIR / file.name / file.name

            console.print_song_step(f"Downloading audio and video (ID: {video_id})…")

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

            console.print_song_success()
            processed += 1

        except YoutubeDownloaderException:
            console.print_song_error("Failed to download audio and video")
            failed += 1

    console.print_summary(processed=processed, failed=failed)
    logger.info("Finished application")


def main() -> None:
    args = _parse_args()
    _setup_logging(args.verbose)
    console = Console(not args.verbose)

    try:
        console.print_header(input_dir=_INPUT_DIR, output_dir=_OUTPUT_DIR)
        asyncio.run(_run(console))
    except KeyboardInterrupt:
        console.print_interrupt()
        logger.info("Interrupted by user")
    except Exception as e:
        console.print_failure(f"Application failed: {e}")
        logger.exception("Application failed")
        raise


if __name__ == "__main__":
    main()
