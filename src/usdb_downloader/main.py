import asyncio
from pathlib import Path
from typing import Final

from usdb_downloader import Parser, YoutubeDownloader

_INPUT_DIR: Final[Path] = Path("./songs/input")
_OUTPUT_DIR: Final[Path] = Path("./songs/output")


async def run() -> None:
    parser = Parser(input_dir=_INPUT_DIR, output_dir=_OUTPUT_DIR)
    youtube_downloader = YoutubeDownloader()

    for file in parser.iter_files():
        parser.write_file(file)
        video_id = file.video_id
        output_path = _OUTPUT_DIR / file.name
        await asyncio.gather(
            youtube_downloader.download_audio(
                video_id=video_id,
                output_path=output_path,
            ),
            youtube_downloader.download_video(
                video_id=video_id,
                output_path=output_path,
            ),
        )


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
