import asyncio
import logging
from pathlib import Path

from usdb_downloader.parser import Parser
from usdb_downloader.youtube_downloader import YoutubeDownloader
from usdb_downloader.console import Console
from usdb_downloader.youtube_downloader import YoutubeDownloaderException

logger = logging.getLogger(__name__)


class App:
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        console: Console,
    ) -> None:
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.console = console
        self.parser = Parser(input_dir=input_dir, output_dir=output_dir)
        self.youtube_downloader = YoutubeDownloader()

    async def run(self) -> None:
        logger.info("Starting application")

        files = list(self.parser.iter_files())

        self.console.print_song_count(len(files))
        if not files:
            return

        processed = 0
        failed = 0

        for idx, file in enumerate(files, 1):
            self.console.print_song_start(idx=idx, total=len(files), name=file.name)

            try:
                self.parser.write_file(file)
                self.console.print_song_step("Parsed song file")

                video_id = file.video_id
                output_path = self.output_dir / file.name / file.name

                with self.console.print_song_step_spinner(
                    f"Downloading audio and video (ID: {video_id})"
                ):
                    await asyncio.gather(
                        self.youtube_downloader.download_audio(
                            video_id=video_id,
                            output_path=output_path,
                        ),
                        self.youtube_downloader.download_video(
                            video_id=video_id,
                            output_path=output_path,
                        ),
                    )

                self.console.print_song_step(
                    f"Downloading audio and video (ID: {video_id})"
                )

                self.console.print_song_success()
                processed += 1

            except YoutubeDownloaderException:
                self.console.print_song_error("Failed to download audio and video")
                failed += 1

        self.console.print_summary(processed=processed, failed=failed)
        logger.info("Finished application")
