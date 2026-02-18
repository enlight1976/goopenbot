"""Session command - manage sessions."""

import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.goopenbot.core.session import SessionStore

console = Console()


async def session_command(list_sessions: bool = False, delete: str = None):
    """Manage sessions."""
    store = SessionStore()

    if delete:
        store.delete(delete)
        console.print(f"[green]Deleted session: {delete}[/green]")
        return

    if not list_sessions:
        console.print("[yellow]Use --list to list sessions or --delete to delete[/yellow]")
        return

    sessions = store.list()

    if not sessions:
        console.print("[yellow]No sessions found[/yellow]")
        return

    table = Table(title="Sessions")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Created", style="dim")
    table.add_column("Updated", style="dim")
    table.add_column("Messages", style="green")
    table.add_column("Model", style="yellow")

    for session in sessions:
        table.add_row(
            session.id[:8] + "...",
            session.created_at[:19],
            session.updated_at[:19],
            str(len(session.messages)),
            session.model,
        )

    console.print(table)
