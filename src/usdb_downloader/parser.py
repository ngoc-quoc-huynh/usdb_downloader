from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Final

from usdb_downloader.models import File

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Parser:
    _ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"(?:a=|v=)([A-Za-z0-9_-]{11})")

    def __init__(self, input_dir: Path, output_dir: Path) -> None:
        self._input_dir = input_dir
        self._output_dir = output_dir
        logger.info(
            "Initialized parser with input directory %s and output directory %s",
            self._input_dir,
            self._output_dir,
        )

    def iter_files(self) -> Generator[File]:
        if not self._input_dir.exists():
            logger.warning("Input directory %s is missing", self._input_dir)
            return

        logger.info("Start scanning input directory %s", self._input_dir)

        count = 0
        for path in self._input_dir.glob("*.txt"):
            song = self._parse_file(path)
            if song:
                yield song
                count += 1

        logger.info("Scanned %d file(s)", count)

    def write_file(self, file: File) -> None:
        output_file = (self._output_dir / file.name / file.name).with_suffix(".txt")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", encoding="utf-8") as f:
            for key, value in file.headers.items():
                f.write(f"#{key}:{value}\n")
            f.writelines(f"{line}\n" for line in file.lyrics)

        logger.info(
            "Wrote file %s to file %s",
            file.name,
            output_file,
        )

    def _parse_file(self, path: Path) -> File | None:
        name = path.stem
        video_id: str | None = None
        headers: dict[str, str] = {}
        lyrics: list[str] = []

        logger.info("Start parsing file %s", name)

        with path.open("r", encoding="utf-8") as src:
            for raw_line in src:
                line = raw_line.strip()

                if not line or line.startswith(("#MP3", "#COVER")):
                    continue

                match line:
                    case l if l.startswith("#VIDEO"):
                        video_id = self._extract_video_id(l)
                    case s if s.startswith("#"):
                        key, _, value = s[1:].partition(":")
                        headers[key.strip()] = value.strip()
                    case _:
                        lyrics.append(line)

        if video_id is None:
            logger.warning("File %s is missing video id", name)
            return None

        headers["COVER"] = f"{name}.jpg"
        headers["MP3"] = f"{name}.mp3"
        headers["VIDEO"] = f"{name}.webm"

        logger.info("Parsed file %s", name)

        return File(
            name=name,
            video_id=video_id,
            headers=headers,
            lyrics=lyrics,
        )

    @staticmethod
    def _extract_video_id(line: str) -> str | None:
        match = Parser._ID_PATTERN.search(line)
        return match.group(1) if match else None
