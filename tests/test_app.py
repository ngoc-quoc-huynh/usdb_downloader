from __future__ import annotations

import asyncio
from contextlib import contextmanager
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest

from usdb_downloader.app import App
from usdb_downloader.parser import File
from usdb_downloader.youtube_downloader import YoutubeDownloaderException

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def input_dir(tmp_path: Path) -> Path:
    return tmp_path / "input"


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    return tmp_path / "output"


@pytest.fixture
def mock_console() -> MagicMock:
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
    mock_console: MagicMock,
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
    mock_console: MagicMock,
) -> None:
    app._parser.iter_files = MagicMock(return_value=iter([]))

    await app.run()

    mock_console.print_song_count.assert_called_once_with(0)
    mock_console.print_summary.assert_not_called()


@pytest.mark.asyncio
async def test_run_reports_unreadable_file_and_processes_valid_song(
    app: App,
    input_dir: Path,
    mock_console: MagicMock,
) -> None:
    input_dir.mkdir()
    (input_dir / "[bold]Unreadable.txt").write_bytes(b"\xff")
    (input_dir / "Valid.txt").write_text(
        "#VIDEO:v=dQw4w9WgXcQ\n",
        encoding="utf-8",
    )
    app._parser.write_file = MagicMock()
    app._youtube_downloader.download_audio = AsyncMock()
    app._youtube_downloader.download_video = AsyncMock()

    await app.run()

    mock_console.print_song_count.assert_called_once_with(1)
    mock_console.print_song_error.assert_called_once_with(
        "Failed to read input file [bold]Unreadable.txt"
    )
    mock_console.print_song_success.assert_called_once()
    mock_console.print_summary.assert_called_once_with(processed=1, failed=1)


@pytest.mark.asyncio
async def test_run_summarizes_unreadable_file_when_all_inputs_fail(
    app: App,
    input_dir: Path,
    mock_console: MagicMock,
) -> None:
    input_dir.mkdir()
    (input_dir / "Unreadable.txt").write_bytes(b"\xff")

    await app.run()

    mock_console.print_song_count.assert_called_once_with(0)
    mock_console.print_song_error.assert_called_once_with(
        "Failed to read input file Unreadable.txt"
    )
    mock_console.print_summary.assert_called_once_with(processed=0, failed=1)


@pytest.mark.asyncio
async def test_run_with_single_file_success(
    app: App,
    mock_console: MagicMock,
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
    mock_console.print_search_cover.assert_called_once_with(
        name="Test - My Song",
        url="https://www.google.com/search?tbm=isch&q=Test%20-%20My%20Song%20Spotify%20Cover",
    )
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
    mock_console.print_search_cover.assert_not_called()
    mock_console.print_summary.assert_called_once_with(
        processed=0,
        failed=1,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("failed_download", ["audio", "video"])
async def test_run_waits_for_sibling_download_after_failure(
    app: App,
    mock_console: MagicMock,
    sample_file: File,
    failed_download: str,
) -> None:
    second_file = File(
        name="Test - Your Song",
        video_id="eQw4w9WgXcQ",
        headers={},
        lyrics=[],
    )
    app._parser.iter_files = MagicMock(return_value=iter([sample_file, second_file]))
    app._parser.write_file = MagicMock()

    release_sibling = asyncio.Event()
    sibling_started = asyncio.Event()
    sibling_finished = asyncio.Event()
    second_song_started = asyncio.Event()

    def track_song_start(*, idx: int, total: int, name: str) -> None:
        if idx == 2:
            second_song_started.set()

    mock_console.print_song_start.side_effect = track_song_start

    async def download_audio(*, video_id: str, output_path: Path) -> None:
        if video_id == sample_file.video_id:
            if failed_download == "audio":
                raise YoutubeDownloaderException("Audio failed")
            sibling_started.set()
            await release_sibling.wait()
            sibling_finished.set()

    async def download_video(*, video_id: str, output_path: Path) -> None:
        if video_id == sample_file.video_id:
            if failed_download == "video":
                raise YoutubeDownloaderException("Video failed")
            sibling_started.set()
            await release_sibling.wait()
            sibling_finished.set()

    app._youtube_downloader.download_audio = download_audio
    app._youtube_downloader.download_video = download_video

    run_task = asyncio.create_task(app.run())
    try:
        await asyncio.wait_for(sibling_started.wait(), timeout=1)
        checkpoint = asyncio.Event()
        asyncio.get_running_loop().call_soon(checkpoint.set)
        await checkpoint.wait()

        assert not second_song_started.is_set()
        assert not mock_console.print_summary.called
        assert not run_task.done()
    finally:
        release_sibling.set()
        await run_task

    assert sibling_finished.is_set()
    assert second_song_started.is_set()
    mock_console.print_summary.assert_called_once_with(processed=1, failed=1)


@pytest.mark.asyncio
async def test_run_propagates_unexpected_error_after_sibling_finishes(
    app: App,
    sample_file: File,
) -> None:
    app._parser.iter_files = MagicMock(return_value=iter([sample_file]))
    release_sibling = asyncio.Event()
    sibling_started = asyncio.Event()
    sibling_finished = asyncio.Event()

    async def download_audio(*, video_id: str, output_path: Path) -> None:
        raise RuntimeError("Unexpected download error")

    async def download_video(*, video_id: str, output_path: Path) -> None:
        sibling_started.set()
        await release_sibling.wait()
        sibling_finished.set()

    app._youtube_downloader.download_audio = download_audio
    app._youtube_downloader.download_video = download_video

    run_task = asyncio.create_task(app.run())
    try:
        await asyncio.wait_for(sibling_started.wait(), timeout=1)
        checkpoint = asyncio.Event()
        asyncio.get_running_loop().call_soon(checkpoint.set)
        await checkpoint.wait()
        assert not run_task.done()
    finally:
        release_sibling.set()

    try:
        await run_task
    except RuntimeError as error:
        assert str(error) == "Unexpected download error"
    else:
        raise AssertionError("Unexpected download errors must propagate")

    assert sibling_finished.is_set()


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
    assert mock_console.print_search_cover.call_count == 2
    assert mock_console.print_song_error.call_count == 1
    mock_console.print_summary.assert_called_once_with(
        processed=2,
        failed=1,
    )
