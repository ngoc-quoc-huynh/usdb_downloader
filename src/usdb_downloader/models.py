from dataclasses import dataclass, field


@dataclass(frozen=True)
class File:
    name: str
    video_id: str
    headers: dict[str, str] = field(default_factory=dict[str, str])
    lyrics: list[str] = field(default_factory=list[str])
