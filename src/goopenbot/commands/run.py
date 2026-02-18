"""Run command - main execution."""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.markdown import Markdown

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.goopenbot.core.provider import OllamaProvider, check_ollama_connection, print_welcome
from src.goopenbot.core.session import Session, SessionStore
from src.goopenbot.tools import get_tool_by_name, get_tools_schema
from src.goopenbot.core.config import load_config

console = Console()

SYSTEM_PROMPT = """You are an AI coding assistant. Your role is to help the user with software development tasks.

You have access to several tools to help you:
- read: Read files to understand code
- write: Create or overwrite files
- edit: Modify existing files
- bash: Execute shell commands
- glob: Find files by pattern
- grep: Search for text in files

IMPORTANT: When you need to use a tool, output ONLY a JSON object like this:
{"name": "tool_name", "arguments": {"param1": "value1", "param2": "value2"}}

Do not include any other text when using tools. Just output the JSON."""


async def run_command(
    message: Optional[str],
    continue_session: bool,
    session_id: Optional[str],
    model: Optional[str],
    dir: Optional[str],
):
    """Main run command."""
    # Check Ollama connection
    if not await check_ollama_connection():
        console.print("[red]Error: Cannot connect to Ollama[/red]")
        console.print("[yellow]Make sure Ollama is running: ollama serve[/yellow]")
        return

    # Change directory if specified
    if dir:
        os.chdir(dir)

    print_welcome()

    # Load config
    config = load_config()

    # Get or create session
    store = SessionStore()

    if session_id:
        session = store.get(session_id)
        if not session:
            console.print(f"[red]Session not found: {session_id}[/red]")
            return
    elif continue_session:
        session = store.get_latest()
        if not session:
            console.print("[yellow]No previous session found[/yellow]")
            console.print("[dim]Starting a new session...[/dim]")
            session = Session.create(model=model or config.provider.model)
    else:
        session = Session.create(model=model or config.provider.model)

    # Initialize provider
    provider = OllamaProvider(model=session.model)

    # Add system message if new session
    if not session.messages:
        session.add_message("system", SYSTEM_PROMPT)

    # If a message was provided, add it and process
    if message:
        session.add_message("user", message)
        await process_message(provider, session, store)
    else:
        # Interactive mode
        await interactive_mode(provider, session, store)

    # Save session
    store.save(session)


async def process_message(
    provider: OllamaProvider,
    session: Session,
    store: SessionStore,
):
    """Process a single message with the AI."""
    tools_schema = get_tools_schema()

    # Convert messages to OpenAI format
    messages = [
        {"role": m["role"], "content": m["content"]}
        for m in session.messages
    ]

    # Get response
    response = await provider.chat(messages, tools=tools_schema, stream=False)

    # Handle response
    choice = response.choices[0]
    message = choice.message

    # Print assistant response
    if message.content:
        console.print("\n[bold cyan]Assistant:[/bold cyan]")
        session.add_message("assistant", message.content)

    # Handle tool calls
    tool_calls = message.tool_calls
    tool_response_text = ""

    # Fallback: Parse tool calls from content if not in tool_calls field
    if not tool_calls and message.content:
        import re
        # Try multiple patterns to find tool calls
        patterns = [
            r'```json\s*(\{.*?\})\s*```',  # JSON in markdown
            r'```\s*(\{.*?\})\s*```',  # JSON in any code block
            r'\{"name":\s*"[^"]+",\s*"arguments":\s*\{.*?\}\}',  # Direct JSON
        ]

        for pattern in patterns:
            json_match = re.search(pattern, message.content, re.DOTALL)
            if json_match:
                try:
                    tool_data = json.loads(json_match.group())
                    if "name" in tool_data and "arguments" in tool_data:
                        tool_calls = [type('obj', (object,), {
                            'id': f"call_{hash(tool_data['name'])}",
                            'function': type('obj', (object,), {
                                'name': tool_data['name'],
                                'arguments': json.dumps(tool_data['arguments'])
                            })()
                        })()]
                        tool_response_text = message.content.replace(json_match.group(), '').strip()
                        break
                except json.JSONDecodeError:
                    pass

    # Print non-tool response text
    if tool_response_text:
        console.print(tool_response_text)

    if tool_calls:
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            args = tool_call.function.arguments

            # Parse arguments
            if isinstance(args, str):
                args = json.loads(args)

            console.print(f"\n[yellow]Using tool: {tool_name}[/yellow]")

            # Get and execute tool
            tool = get_tool_by_name(tool_name)
            if tool:
                result = tool().execute(**args)
                console.print(f"\n[dim]{result.get('title', tool_name)}[/dim]")
                console.print(result.get("output", "")[:500])

                # Add tool result
                session.add_tool_result(tool_call.id, json.dumps(result))
            else:
                console.print(f"[red]Tool not found: {tool_name}[/red]")

        # Save after tool execution
        store.save(session)

        # Continue conversation
        await process_message(provider, session, store)


async def interactive_mode(
    provider: OllamaProvider,
    session: Session,
    store: SessionStore,
):
    """Run interactive mode."""
    console.print("\n[dim]Interactive mode. Type 'exit' or 'quit' to end session.[/dim]\n")

    while True:
        try:
            user_input = console.input("[bold green]> [/bold green]")
            if user_input.lower() in ("exit", "quit"):
                console.print("[dim]Saving session...[/dim]")
                store.save(session)
                console.print(f"[green]Session saved: {session.id}[/green]")
                break

            if not user_input.strip():
                continue

            session.add_message("user", user_input)
            await process_message(provider, session, store)

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Saving session...[/yellow]")
            store.save(session)
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            store.save(session)
            break