from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest

from usdb_downloader.app import App
from usdb_downloader.parser import File
from usdb_downloader.youtube_downloader import YoutubeDownloaderException

if TYPE_CHECKING:
    from pathlib import Path

type MockConsole = MagicMock


@pytest.fixture
def input_dir(tmp_path: Path) -> Path:
    return tmp_path / "input"


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    return tmp_path / "output"


@pytest.fixture
def mock_console() -> MockConsole:
    console = MagicMock()

    @contextmanager
    def spinner_ctx(message: str):
        yield

    console.print_song_step_spinner.side_effect = spinner_ctx

    return console


@pytest.fixture
def app(
    input_dir: Path,
    output_dir: Path,
    mock_console: MockConsole,
) -> App:
    return App(input_dir=input_dir, output_dir=output_dir, console=mock_console)


@pytest.fixture
def sample_file() -> File:
    return File(
        name="Test - My Song",
        video_id="dQw4w9WgXcQ",
        headers={
            "ARTIST": "Test",
            "COVER": "Test - My Song.jpg",
            "MP3": "Test - My Song.mp3",
            "TITLE": "My Song",
            "VIDEO": "Test - My Song.webm",
        },
        lyrics=[
            ": 0 1 2 My",
            ": 3 4 5 Song",
        ],
    )


@pytest.mark.asyncio
async def test_run_with_no_files(
    app: App,
    mock_console: MockConsole,
) -> None:
    app._parser.iter_files = MagicMock(return_value=iter([]))

    await app.run()

    mock_console.print_song_count.assert_called_once_with(0)
    mock_console.print_summary.assert_not_called()


@pytest.mark.asyncio
async def test_run_with_single_file_success(
    app: App,
    mock_console: MockConsole,
    sample_file: File,
    output_dir: Path,
) -> None:
    app._parser.iter_files = MagicMock(return_value=iter([sample_file]))
    app._parser.write_file = MagicMock()
    app._youtube_downloader.download_audio = AsyncMock()
    app._youtube_downloader.download_video = AsyncMock()

    await app.run()

    mock_console.print_song_count.assert_called_once_with(1)
    mock_console.print_song_start.assert_called_once_with(
        idx=1,
        total=1,
        name="Test - My Song",
    )
    app._parser.write_file.assert_called_once_with(sample_file)
    mock_console.print_song_step.assert_any_call("Parsed song file")

    expected_output_path = output_dir / "Test - My Song" / "Test - My Song"
    app._youtube_downloader.download_audio.assert_called_once_with(
        video_id="dQw4w9WgXcQ",
        output_path=expected_output_path,
    )
    app._youtube_downloader.download_video.assert_called_once_with(
        video_id="dQw4w9WgXcQ",
        output_path=expected_output_path,
    )

    mock_console.print_song_step_spinner.assert_called_once_with(
        "Downloading audio and video (ID: dQw4w9WgXcQ)"
    )
    mock_console.print_song_step.assert_any_call(
        "Downloading audio and video (ID: dQw4w9WgXcQ)"
    )

    mock_console.print_song_success.assert_called_once()
    mock_console.print_summary.assert_called_once_with(
        processed=1,
        failed=0,
    )


@pytest.mark.asyncio
async def test_run_with_youtube_downloader_exception(
    app: App,
    mock_console: MagicMock,
    sample_file: File,
) -> None:
    app._parser.iter_files = MagicMock(return_value=iter([sample_file]))
    app._parser.write_file = MagicMock()
    app._youtube_downloader.download_audio = AsyncMock(
        side_effect=YoutubeDownloaderException("Download failed")
    )
    app._youtube_downloader.download_video = AsyncMock()

    await app.run()

    mock_console.print_song_count.assert_called_once_with(1)
    mock_console.print_song_error.assert_called_once_with(
        "Failed to download audio and video"
    )
    mock_console.print_song_success.assert_not_called()
    mock_console.print_summary.assert_called_once_with(
        processed=0,
        failed=1,
    )


@pytest.mark.asyncio
async def test_run_with_multiple_files_mixed_results(
    app: App,
    mock_console: MagicMock,
    output_dir: Path,
) -> None:
    file1 = File(
        name="Test - My Song",
        video_id="dQw4w9WgXcQ",
        headers={
            "ARTIST": "Test",
            "COVER": "Test - My Song.jpg",
            "MP3": "Test - My Song.mp3",
            "TITLE": "My Song",
            "VIDEO": "Test - My Song.webm",
        },
        lyrics=[": 0 1 2 My"],
    )
    file2 = File(
        name="Test - Your Song",
        video_id="eQw4w9WgXcQ",
        headers={
            "ARTIST": "Test",
            "COVER": "Test - Your Song.jpg",
            "MP3": "Test - Your Song.mp3",
            "TITLE": "Your Song",
            "VIDEO": "Test - Your Song.webm",
        },
        lyrics=[": 0 1 2 Two"],
    )
    file3 = File(
        name="Test - Our Song",
        video_id="fQw4w9WgXcQ",
        headers={
            "ARTIST": "Test",
            "COVER": "Test - Our Song.jpg",
            "MP3": "Test - Our Song.mp3",
            "TITLE": "Our Song",
            "VIDEO": "Test - Our Song.webm",
        },
        lyrics=[": 0 1 2 Three"],
    )

    app._parser.iter_files = MagicMock(return_value=iter([file1, file2, file3]))
    app._parser.write_file = MagicMock()

    app._youtube_downloader.download_audio = AsyncMock(
        side_effect=[
            None,  # Success for file1
            YoutubeDownloaderException("Download failed"),  # Failure for file2
            None,  # Success for file3
        ]
    )
    app._youtube_downloader.download_video = AsyncMock()

    await app.run()

    mock_console.print_song_count.assert_called_once_with(3)
    assert mock_console.print_song_start.call_count == 3
    mock_console.print_song_start.assert_any_call(
        idx=1,
        total=3,
        name="Test - My Song",
    )
    mock_console.print_song_start.assert_any_call(
        idx=2,
        total=3,
        name="Test - Your Song",
    )
    mock_console.print_song_start.assert_any_call(
        idx=3,
        total=3,
        name="Test - Our Song",
    )

    assert mock_console.print_song_success.call_count == 2
    assert mock_console.print_song_error.call_count == 1
    mock_console.print_summary.assert_called_once_with(
        processed=2,
        failed=1,
    )
