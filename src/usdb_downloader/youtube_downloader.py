import asyncio
import logging
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final, cast
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

logger = logging.getLogger(__name__)


class YoutubeDownloaderException(Exception):
    """Custom exception for YoutubeDownloader errors."""


class YoutubeDownloader:
    _ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"(?:a=|v=)([A-Za-z0-9_-]{11})")
    _DEFAULT_COMMON_OPTS: Final[Mapping[str, Any]] = {
        "quiet": True,
        "no_warnings": True,
        "concurrent_fragment_downloads": 5,
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

    @classmethod
    def extract_video_id(cls, line: str) -> str | None:
        match = cls._ID_PATTERN.search(line)
        return match.group(1) if match else None

    async def download_video(self, video_id: str, output_path: Path) -> None:
        try:
            await asyncio.to_thread(
                self._download,
                video_id,
                output_path,
                self._DEFAULT_VIDEO_OPTS,
            )
        except DownloadError as e:
            raise YoutubeDownloaderException(
                f"Failed to download video {video_id}: {e}"
            ) from e

    async def download_audio(self, video_id: str, output_path: Path) -> None:
        try:
            await asyncio.to_thread(
                self._download,
                video_id,
                output_path,
                self._DEFAULT_AUDIO_OPTS,
            )
        except DownloadError as e:
            raise YoutubeDownloaderException(
                f"Failed to download audio {video_id}: {e}"
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

        logger.info("Starting download: %s -> %s", url, output_path)
        with YoutubeDL(cast(Any, opts)) as ydl:
            ydl.download([url])
        logger.info("Successfully downloaded: %s", video_id)
