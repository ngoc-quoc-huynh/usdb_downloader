from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from usdb_downloader.parser import File, Parser

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def input_path(tmp_path: Path) -> Path:
    return tmp_path / "input"


@pytest.fixture
def output_path(tmp_path: Path) -> Path:
    return tmp_path / "output"


@pytest.fixture
def parser(input_path: Path, output_path: Path) -> Parser:
    input_path.mkdir()
    return Parser(input_dir=input_path, output_dir=output_path)


def _create_test_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_iter_files_yields_nothing(parser: Parser) -> None:
    assert list(parser.iter_files()) == []


def test_iter_files_yields_single_file(parser: Parser, input_path: Path) -> None:
    test_file_path = input_path / "Test - My Song.txt"
    _create_test_file(
        path=test_file_path,
        content="""
    #ARTIST:Test
    #TITLE:My Song
    #VIDEO:v=dQw4w9WgXcQ
    : 0 1 2 My
    : 3 4 5 Song
    """,
    )

    files = list(parser.iter_files())

    assert len(files) == 1
    assert files[0] == File(
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


def test_iter_files_yields_multiple_files(parser: Parser, input_path: Path) -> None:
    _create_test_file(
        path=input_path / "Test - My Song.txt",
        content="""
    #ARTIST:Test
    #TITLE:My Song
    #VIDEO:v=dQw4w9WgXcQ
    : 0 1 2 My
    : 3 4 5 Song
    """,
    )
    _create_test_file(
        path=input_path / "Test - Your Song.txt",
        content="""
       #ARTIST:Test
       #TITLE:Your Song
       #VIDEO:v=eQw4w9WgXcQ
       : 0 1 2 Your
       : 3 4 5 Song
       """,
    )

    files = list(parser.iter_files())

    assert len(files) == 2
    expected_song1 = File(
        name="Test - Your Song",
        video_id="eQw4w9WgXcQ",
        headers={
            "ARTIST": "Test",
            "COVER": "Test - Your Song.jpg",
            "MP3": "Test - Your Song.mp3",
            "TITLE": "Your Song",
            "VIDEO": "Test - Your Song.webm",
        },
        lyrics=[
            ": 0 1 2 Your",
            ": 3 4 5 Song",
        ],
    )
    assert expected_song1 in files
    expected_song2 =File(
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
    assert expected_song2 in files


def test_write_file(parser: Parser, output_path: Path) -> None:
    file = File(
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

    parser.write_file(file)

    output_file = output_path / "Test - My Song" / "Test - My Song.txt"
    assert output_file.exists()

    lines = output_file.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "#ARTIST:Test"
    assert lines[1] == "#COVER:Test - My Song.jpg"
    assert lines[2] == "#MP3:Test - My Song.mp3"
    assert lines[3] == "#TITLE:My Song"
    assert lines[4] == "#VIDEO:Test - My Song.webm"
    assert lines[5] == ": 0 1 2 My"
    assert lines[6] == ": 3 4 5 Song"


def test_parse_file_correctly(
    parser: Parser,
    input_path: Path,
) -> None:
    test_file_path = input_path / "Test - My Song.txt"
    _create_test_file(
        path=test_file_path,
        content="""
#ARTIST:Test
#TITLE:My Song
#YEAR:2025
#LANGUAGE:English
#BPM:120
#GAP:390
#VIDEO:v=dQw4w9WgXcQ
: 0 1 2 My
: 3 4 5 Song
""",
    )

    file = parser._parse_file(test_file_path)

    assert file == File(
        name="Test - My Song",
        video_id="dQw4w9WgXcQ",
        headers={
            "ARTIST": "Test",
            "BPM": "120",
            "COVER": "Test - My Song.jpg",
            "GAP": "390",
            "LANGUAGE": "English",
            "MP3": "Test - My Song.mp3",
            "TITLE": "My Song",
            "VIDEO": "Test - My Song.webm",
            "YEAR": "2025",
        },
        lyrics=[
            ": 0 1 2 My",
            ": 3 4 5 Song",
        ],
    )


def test_parse_file_overwrites_existing_headers(
    parser: Parser,
    input_path: Path,
) -> None:
    test_file_path = input_path / "Test - My Song.txt"
    _create_test_file(
        path=test_file_path,
        content="""
#ARTIST:Test
#TITLE:My Song
#YEAR:2025
#LANGUAGE:English
#BPM:120
#GAP:390
#VIDEO:v=dQw4w9WgXcQ
#COVER:Test - Your Song.jpg
#MP3:Test - Your Song.mp3
: 0 1 2 My
: 3 4 5 Song
""",
    )

    file = parser._parse_file(test_file_path)

    assert file == File(
        name="Test - My Song",
        video_id="dQw4w9WgXcQ",
        headers={
            "ARTIST": "Test",
            "BPM": "120",
            "COVER": "Test - My Song.jpg",
            "GAP": "390",
            "LANGUAGE": "English",
            "MP3": "Test - My Song.mp3",
            "TITLE": "My Song",
            "VIDEO": "Test - My Song.webm",
            "YEAR": "2025",
        },
        lyrics=[
            ": 0 1 2 My",
            ": 3 4 5 Song",
        ],
    )


def test_parse_file_returns_none_when_video_id_is_missing(
    parser: Parser,
    input_path: Path,
) -> None:
    test_file_path = input_path / "Test - My Song.txt"
    _create_test_file(
        path=test_file_path,
        content="""
    #ARTIST:Test
    #TITLE:My Song
    #YEAR:2025
    #LANGUAGE:English
    #BPM:120
    #GAP:390
    : 0 1 2 My
    : 3 4 5 Song
    """,
    )

    file = parser._parse_file(test_file_path)

    assert file is None


@pytest.mark.parametrize(
    "line,expected",
    [
        ("#VIDEO:a=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("#VIDEO:v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("#VIDEO:a=dQw4w9WgXcQ, other properties", "dQw4w9WgXcQ"),
        ("#VIDEO: no id here", None),
    ],
)
def test_extract_video_id(line: str, expected: str | None) -> None:
    assert Parser._extract_video_id(line) == expected
