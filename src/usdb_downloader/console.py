from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from rich.console import Console as RichConsole
from rich.live import Live
from rich.spinner import Spinner

if TYPE_CHECKING:
    from collections.abc import Generator


class Console:
    def __init__(self, enabled: bool) -> None:
        self._console = RichConsole()
        self._enabled = enabled

    def _print(self, *args: Any, **kwargs: Any) -> None:
        if self._enabled:
            self._console.print(*args, **kwargs)

    def print_header(self, input_dir: Any, output_dir: Any) -> None:
        self._print("\n[bold cyan]🎵 USDB Downloader[/bold cyan]")
        self._print(f"[dim]Input directory: {input_dir}[/dim]")
        self._print(f"[dim]Output directory: {output_dir}[/dim]\n")

    def print_song_count(self, count: int) -> None:
        if count > 0:
            self._print(f"[green]✓ Found {count} song(s) to process[/green]\n")
        else:
            self._print("[yellow]⚠ No valid song files found to process[/yellow]")

    def print_song_start(self, idx: int, total: int, name: str) -> None:
        self._print(f"[bold]Processing {idx}/{total}:[/bold] [cyan]{name}[/cyan]")

    def print_song_step(self, message: str) -> None:
        self._print(f"  ├─ [dim]{message}[/dim]")

    def print_song_success(self, message: str = "Completed") -> None:
        self._print(f"  └─ [green]✓ {message}[/green]\n")

    def print_song_error(self, message: str) -> None:
        self._print(f"  └─ [red]✗ {message}[/red]\n")

    def print_summary(self, processed: int, failed: int) -> None:
        self._print("[bold]Summary:[/bold]")
        self._print(f"  [green]✓ Successful: {processed}[/green]")
        if failed > 0:
            self._print(f"  [red]✗ Failed: {failed}[/red]")
        self._print()

    def print_interrupt(self) -> None:
        self._print("\n[yellow]⚠ Interrupted by user[/yellow]")

    def print_failure(self, message: str) -> None:
        self._print(f"\n[red]✗ {message}[/red]")

    @contextmanager
    def print_song_step_spinner(self, message: str) -> Generator[None]:
        if self._enabled:
            with Live(
                Spinner("dots", text=f"├─ [dim]{message}[/dim]"),
                console=self._console,
                transient=True,
            ):
                yield
        else:
            yield

    def print_search_cover(self, name: str, url: str) -> None:
        self._print(f"  ├─ [dim]Search for cover for {name}[/dim]")
        self._print(f"  │   └─ [link={url}]{url}[/link]")
