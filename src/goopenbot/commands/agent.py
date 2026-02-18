"""Agent command - manage agents."""

import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.goopenbot.core.config import get_config_dir

console = Console()


async def agent_command(list_agents: bool = False, create: bool = False, name: str = None):
    """Manage agents."""
    agents_dir = get_config_dir() / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    if create:
        if not name:
            console.print("[red]Error: --name is required when creating an agent[/red]")
            return

        agent_file = agents_dir / f"{name}.md"
        if agent_file.exists():
            console.print(f"[red]Agent already exists: {name}[/red]")
            return

        content = f"""---
name: {name}
model: qwen2.5-coder:7b
tools:
  - read
  - write
  - bash
  - glob
  - grep
---

# {name} Agent

Describe your agent here.
"""
        agent_file.write_text(content)
        console.print(f"[green]Created agent: {name}[/green]")
        return

    if not list_agents:
        console.print("[yellow]Use --list to list agents or --create to create one[/yellow]")
        return

    agents = list(agents_dir.glob("*.md"))

    if not agents:
        console.print("[yellow]No agents found[/yellow]")
        console.print("[dim]Create one: python goopenbot.py agent --create --name myagent[/dim]")
        return

    table = Table(title="Agents")
    table.add_column("Name", style="cyan")
    table.add_column("File", style="dim")

    for agent in agents:
        table.add_row(agent.stem, agent.name)

    console.print(table)
