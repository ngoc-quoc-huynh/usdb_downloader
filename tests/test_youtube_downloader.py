from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from yt_dlp.utils import DownloadError

from usdb_downloader.youtube_downloader import (
    YoutubeDownloader,
    YoutubeDownloaderException,
)

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


@pytest.fixture
def youtube_downloader() -> YoutubeDownloader:
    return YoutubeDownloader()


@pytest.fixture
def mock_yt_dlp() -> Generator[MagicMock]:
    with patch("usdb_downloader.youtube_downloader.YoutubeDL") as mock:
        yield mock


@pytest.fixture
def video_id() -> str:
    return "dQw4w9WgXcQ"


@pytest.fixture
def output_path(tmp_path: Path) -> Path:
    return tmp_path / "result"


@pytest.mark.asyncio
async def test_download_video_correctly(
    youtube_downloader: YoutubeDownloader,
    mock_yt_dlp: MagicMock,
    output_path: Path,
    video_id: str,
) -> None:
    yt_dlp_instance = mock_yt_dlp.return_value
    yt_dlp_instance.__enter__.return_value = yt_dlp_instance

    await youtube_downloader.download_video(
        video_id=video_id,
        output_path=output_path,
    )

    mock_yt_dlp.assert_called_once()
    args, _ = mock_yt_dlp.call_args
    opts = args[0]
    assert opts["format"] == "bestvideo[ext=webm]/bestvideo"
    assert opts["merge_output_format"] == "webm"
    assert opts["outtmpl"] == f"{output_path}.%(ext)s"

    yt_dlp_instance.download.assert_called_once_with(
        [f"https://www.youtube.com/watch?v={video_id}"]
    )


@pytest.mark.asyncio
async def test_download_video_raises_exception_on_download_error(
    youtube_downloader: YoutubeDownloader,
    mock_yt_dlp: MagicMock,
    output_path: Path,
    video_id: str,
) -> None:
    yt_dlp_instance = mock_yt_dlp.return_value
    yt_dlp_instance.__enter__.return_value = yt_dlp_instance
    yt_dlp_instance.download.side_effect = DownloadError("Download failed")

    with pytest.raises(YoutubeDownloaderException) as e:
        await youtube_downloader.download_video(
            video_id=video_id, output_path=output_path
        )

    assert "Failed to download video: Download failed" in str(e.value)


@pytest.mark.asyncio
async def test_download_audio_correctly(
    youtube_downloader: YoutubeDownloader,
    mock_yt_dlp: MagicMock,
    output_path: Path,
    video_id: str,
) -> None:
    yt_dlp_instance = mock_yt_dlp.return_value
    yt_dlp_instance.__enter__.return_value = yt_dlp_instance

    await youtube_downloader.download_audio(
        video_id=video_id,
        output_path=output_path,
    )

    mock_yt_dlp.assert_called_once()
    args, _ = mock_yt_dlp.call_args
    opts = args[0]
    assert opts["format"] == "bestaudio[ext=m4a]/bestaudio"
    assert opts["postprocessors"] == [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ]
    assert opts["outtmpl"] == f"{output_path}.%(ext)s"

    yt_dlp_instance.download.assert_called_once_with(
        [f"https://www.youtube.com/watch?v={video_id}"]
    )


@pytest.mark.asyncio
async def test_download_audio_raises_exception_on_download_error(
    youtube_downloader: YoutubeDownloader,
    mock_yt_dlp: MagicMock,
    output_path: Path,
    video_id: str,
) -> None:
    yt_dlp_instance = mock_yt_dlp.return_value
    yt_dlp_instance.__enter__.return_value = yt_dlp_instance
    yt_dlp_instance.download.side_effect = DownloadError("Download failed")

    with pytest.raises(YoutubeDownloaderException) as exc_info:
        await youtube_downloader.download_audio(
            video_id=video_id, output_path=output_path
        )

    assert "Failed to download audio: Download failed" in str(exc_info.value)
