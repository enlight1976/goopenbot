"""Main CLI entry point for goopenbot."""

import asyncio
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from goopenbot.commands.run import run_command
from goopenbot.commands.models import models_command
from goopenbot.commands.session import session_command
from goopenbot.commands.agent import agent_command
from goopenbot.core.provider import check_ollama_connection, print_welcome
from goopenbot.core.config import load_config

console = Console()

app = typer.Typer(
    name="goopenbot",
    help="AI-powered development tool with local Ollama",
    add_completion=False,
)


@app.command()
def run(
    message: Optional[str] = typer.Argument(None, help="Message to send to the AI"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue the last session"),
    session_id: Optional[str] = typer.Option(None, "--session", "-s", help="Continue a specific session"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use"),
    dir: Optional[str] = typer.Option(None, "--dir", "-d", help="Working directory"),
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
    delete: Optional[str] = typer.Option(None, "--delete", help="Delete a session by ID"),
):
    """Manage sessions."""
    asyncio.run(session_command(list_sessions, delete))


@app.command()
def agent(
    list_agents: bool = typer.Option(False, "--list", "-l", help="List all agents"),
    create: bool = typer.Option(False, "--create", "-c", help="Create a new agent"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Agent name"),
):
    """Manage agents."""
    asyncio.run(agent_command(list_agents, create, name))


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """goopenbot - AI-powered development tool."""
    if ctx.invoked_subcommand is None:
        print_welcome()
        console.print("\n[bold]Usage:[/bold]")
        console.print("  goopenbot run <message>    Run with a message")
        console.print("  goopenbot models          List available models")
        console.print("  goopenbot session --list  List sessions")
        console.print("  goopenbot --help          Show this help")


if __name__ == "__main__":
    app()
