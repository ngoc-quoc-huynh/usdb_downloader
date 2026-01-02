from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Final, cast

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from usdb_downloader.silent_logger import SilentLogger

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

logger = logging.getLogger(__name__)


class YoutubeDownloaderException(Exception):
    """Custom exception for YoutubeDownloader errors."""


class YoutubeDownloader:
    _DEFAULT_COMMON_OPTS: Final[Mapping[str, Any]] = {
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "no_color": True,
        "concurrent_fragment_downloads": 5,
        "logger": SilentLogger(),
    }
    _DEFAULT_VIDEO_OPTS: Final[Mapping[str, Any]] = {
        **_DEFAULT_COMMON_OPTS,
        "format": "bestvideo[ext=webm]/bestvideo",
        "merge_output_format": "webm",
    }
    _DEFAULT_AUDIO_OPTS: Final[Mapping[str, Any]] = {
        **_DEFAULT_COMMON_OPTS,
        "format": "bestaudio[ext=m4a]/bestaudio",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    async def download_video(self, video_id: str, output_path: Path) -> None:
        try:
            logger.info("Starting download video with id %s", video_id)
            await asyncio.to_thread(
                self._download,
                video_id,
                output_path,
                self._DEFAULT_VIDEO_OPTS,
            )
            logger.info("Successfully downloaded video with id %s", video_id)
        except DownloadError as e:
            error_msg = str(e)
            logger.error("Failed to download video with id %s: %s", video_id, error_msg)
            raise YoutubeDownloaderException(
                f"Failed to download video: {error_msg}"
            ) from e

    async def download_audio(self, video_id: str, output_path: Path) -> None:
        try:
            logger.info("Starting download audio with id %s", video_id)
            await asyncio.to_thread(
                self._download,
                video_id,
                output_path,
                self._DEFAULT_AUDIO_OPTS,
            )
            logger.info("Successfully downloaded audio with id %s", video_id)
        except DownloadError as e:
            error_msg = str(e)
            logger.error("Failed to download audio with id %s: %s", video_id, error_msg)
            raise YoutubeDownloaderException(
                f"Failed to download audio: {error_msg}"
            ) from e

    @classmethod
    def _build_download_url(cls, video_id: str) -> str:
        return f"https://www.youtube.com/watch?v={video_id}"

    @classmethod
    def _download(
        cls,
        video_id: str,
        output_path: Path,
        base_opts: Mapping[str, Any],
    ) -> None:
        url = cls._build_download_url(video_id)
        opts = {
            **base_opts,
            "outtmpl": str(output_path.with_suffix(".%(ext)s")),
        }

        with YoutubeDL(cast("Any", opts)) as ydl:
            ydl.download([url])
