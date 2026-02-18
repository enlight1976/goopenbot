"""goopenbot - AI-powered development tool with local Ollama."""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

import typer
from rich.console import Console

from src.goopenbot.commands.run import run_command
from src.goopenbot.commands.models import models_command
from src.goopenbot.commands.session import session_command
from src.goopenbot.commands.agent import agent_command
from src.goopenbot.core.provider import check_ollama_connection, print_welcome
from src.goopenbot.core.config import load_config

console = Console()

app = typer.Typer(
    name="goopenbot",
    help="AI-powered development tool with local Ollama",
    add_completion=False,
)


@app.command()
def run(
    message: str = typer.Argument(None, help="Message to send to the AI"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue the last session"),
    session_id: str = typer.Option(None, "--session", "-s", help="Continue a specific session"),
    model: str = typer.Option(None, "--model", "-m", help="Model to use"),
    dir: str = typer.Option(None, "--dir", "-d", help="Working directory"),
):
    """Run goopenbot with a message (main command)."""
    asyncio.run(run_command(message, continue_session, session_id, model, dir))


@app.command()
def models(
    refresh: bool = typer.Option(False, "--refresh", help="Refresh model list"),
):
    """List available models from Ollama."""
    asyncio.run(models_command(refresh))


@app.command()
def session(
    list_sessions: bool = typer.Option(False, "--list", "-l", help="List all sessions"),
    delete: str = typer.Option(None, "--delete", help="Delete a session by ID"),
):
    """Manage sessions."""
    asyncio.run(session_command(list_sessions, delete))


@app.command()
def agent(
    list_agents: bool = typer.Option(False, "--list", "-l", help="List all agents"),
    create: bool = typer.Option(False, "--create", "-c", help="Create a new agent"),
    name: str = typer.Option(None, "--name", "-n", help="Agent name"),
):
    """Manage agents."""
    asyncio.run(agent_command(list_agents, create, name))


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """goopenbot - AI-powered development tool."""
    if ctx.invoked_subcommand is None:
        print_welcome()
        console.print("\n[bold]Usage:[/bold]")
        console.print("  python goopenbot.py run <message>    Run with a message")
        console.print("  python goopenbot.py models          List available models")
        console.print("  python goopenbot.py session --list  List sessions")
        console.print("  python goopenbot.py --help          Show this help")


if __name__ == "__main__":
    app()
