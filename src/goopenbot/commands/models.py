"""Models command - list available Ollama models."""

import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.goopenbot.core.provider import OllamaProvider, check_ollama_connection

console = Console()


async def models_command(refresh: bool = False):
    """List available models from Ollama."""
    if not await check_ollama_connection():
        console.print("[red]Error: Cannot connect to Ollama[/red]")
        console.print("[yellow]Make sure Ollama is running: ollama serve[/yellow]")
        return

    provider = OllamaProvider()
    models = await provider.list_models()

    if not models:
        console.print("[yellow]No models found[/yellow]")
        console.print("[dim]Download a model: ollama pull llama3[/dim]")
        return

    table = Table(title="Available Ollama Models")
    table.add_column("Model", style="cyan")
    table.add_column("ID", style="dim")

    for model in models:
        table.add_row(model["name"], model["id"])

    console.print(table)
    console.print(f"\n[dim]Using model: {provider.model}[/dim]")
