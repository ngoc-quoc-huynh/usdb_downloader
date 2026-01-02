from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from usdb_downloader.console import Console
from usdb_downloader.parser import Parser
from usdb_downloader.youtube_downloader import (
    YoutubeDownloader,
    YoutubeDownloaderException,
)

if TYPE_CHECKING:
    from pathlib import Path

    from usdb_downloader.console import Console

logger = logging.getLogger(__name__)


class App:
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        console: Console,
    ) -> None:
        self._input_dir = input_dir
        self._output_dir = output_dir
        self._console = console
        self._parser = Parser(input_dir=input_dir, output_dir=output_dir)
        self._youtube_downloader = YoutubeDownloader()

    async def run(self) -> None:
        logger.info("Starting application")

        files = list(self._parser.iter_files())

        self._console.print_song_count(len(files))
        if not files:
            return

        processed = 0
        failed = 0

        for idx, file in enumerate(files, 1):
            self._console.print_song_start(idx=idx, total=len(files), name=file.name)

            try:
                self._parser.write_file(file)
                self._console.print_song_step("Parsed song file")

                video_id = file.video_id
                output_path = self._output_dir / file.name / file.name

                with self._console.print_song_step_spinner(
                    f"Downloading audio and video (ID: {video_id})"
                ):
                    await asyncio.gather(
                        self._youtube_downloader.download_audio(
                            video_id=video_id,
                            output_path=output_path,
                        ),
                        self._youtube_downloader.download_video(
                            video_id=video_id,
                            output_path=output_path,
                        ),
                    )

                self._console.print_song_step(
                    f"Downloading audio and video (ID: {video_id})"
                )

                self._console.print_song_success()
                processed += 1
            except YoutubeDownloaderException:
                self._console.print_song_error("Failed to download audio and video")
                failed += 1

        self._console.print_summary(processed=processed, failed=failed)
        logger.info("Finished application")
