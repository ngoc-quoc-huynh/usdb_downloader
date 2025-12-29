import re
import logging
from dataclasses import field, dataclass
from pathlib import Path
from typing import Final, Generator

logger = logging.getLogger(__name__)


@dataclass
class File:
    name: str
    video_id: str
    headers: dict[str, str] = field(default_factory=dict[str, str])
    lyrics: list[str] = field(default_factory=list[str])


class Parser:
    _ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"(?:a=|v=)([A-Za-z0-9_-]{11})")

    def __init__(self, input_dir: Path, output_dir: Path) -> None:
        self.input_dir = input_dir
        self.output_dir = output_dir

    def iter_files(self) -> Generator[File, None, None]:
        if not self.input_dir.exists():
            logger.warning(f"Input directory does not exist: {self.input_dir}")
            return

        for path in self.input_dir.glob("*.txt"):
            song = self._parse_file(path)
            if song:
                yield song

    def write_file(self, file: File) -> None:
        output_file = self.output_dir / f"{file.name}.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            for key, value in file.headers.items():
                f.write(f"#{key}:{value}\n")
            f.writelines(f"{line}\n" for line in file.lyrics)

        logger.info(f"Wrote file {output_file}")

    def _parse_file(self, path: Path) -> File | None:
        name = path.stem
        video_id: str | None = None
        headers: dict[str, str] = {}
        lyrics: list[str] = []

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
            return None

        headers["COVER"] = f"{name}.jpg"
        headers["MP3"] = f"{name}.mp3"
        headers["VIDEO"] = f"{name}.webm"
        logger.info(f"Parsed file {name}")

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
