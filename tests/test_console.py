from __future__ import annotations

from io import StringIO

from rich.console import Console as RichConsole

from usdb_downloader.console import Console


def test_print_song_error_displays_markup_like_filename_literally() -> None:
    output = StringIO()
    console = Console(enabled=True)
    console._console = RichConsole(file=output, force_terminal=False)

    console.print_song_error("Failed to read input file [bold]Unreadable[/bold].txt")

    assert "Failed to read input file [bold]Unreadable[/bold].txt" in output.getvalue()
