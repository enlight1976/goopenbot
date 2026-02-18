"""Ollama provider integration using OpenAI-compatible API."""

import json
from typing import Any, Optional

from openai import AsyncOpenAI
from rich.console import Console
from rich.panel import Panel

from .config import load_config

console = Console()

# Models that support tool calling
TOOL_SUPPORTED_MODELS = [
    "qwen2.5-coder",
    "qwen2.5",
    "qwen3",
    "llama3.1",
    "llama3.3",
    "gemma3",
    "glm-4",
    "deepseek-coder",
]

TOOL_CAPABLE_MODELS = [
    "qwen2.5-coder",
    "qwen2.5",
    "qwen3",
    "llama3.1",
    "llama3.2",
    "llama3.3",
    "gemma2",
    "gemma3",
    "mistral",
    "deepseek-coder",
    "glm",
]


def supports_tools(model_name: str) -> bool:
    """Check if a model supports tool calling."""
    model_lower = model_name.lower()
    return any(capable in model_lower for capable in TOOL_CAPABLE_MODELS)


class OllamaProvider:
    """Ollama provider for local LLM inference."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        config = load_config()
        self.base_url = base_url or config.provider.base_url
        self.model = model or config.provider.model
        self.api_key = api_key or config.provider.api_key or "not-needed"
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
        stream: bool = True,
    ) -> Any:
        """Send a chat request to Ollama."""
        params: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
        }

        # Only add tools if the model supports them
        if tools and supports_tools(self.model):
            params["tools"] = tools
        elif tools:
            console.print(
                f"[yellow]Warning: Model {self.model} may not support tools. "
                f"Using a model like qwen2.5-coder or llama3.1 for tool support.[/yellow]"
            )

        return await self.client.chat.completions.create(**params)

    async def list_models(self) -> list[dict[str, Any]]:
        """List available models from Ollama."""
        try:
            import httpx

            base = self.base_url.replace("/v1", "")
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [
                        {"id": m["name"], "name": m["name"]}
                        for m in data.get("models", [])
                    ]
        except Exception as e:
            console.print(f"[red]Error listing models: {e}[/red]")
        return []


async def select_model() -> str:
    """Interactive model selection from available Ollama models."""
    provider = OllamaProvider()
    models = await provider.list_models()

    if not models:
        console.print("[yellow]No models found. Using default: qwen2.5-coder:7b[/yellow]")
        return "qwen2.5-coder:7b"

    console.print("\n[bold]Available models (tool-capable marked with *):[/bold]")
    for i, model in enumerate(models, 1):
        marker = " *" if supports_tools(model["name"]) else ""
        console.print(f"  {i}. {model['name']}{marker}")

    # Find a capable model
    for model in models:
        if supports_tools(model["name"]):
            console.print(f"\n[dim]Using: {model['name']}[/dim]")
            return model["name"]

    console.print(f"\n[yellow]No tool-capable model found. Using: {provider.model}[/yellow]")
    return provider.model


async def check_ollama_connection() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        import httpx

        base = OllamaProvider().base_url.replace("/v1", "")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base}/api/tags", timeout=5.0)
            return response.status_code == 200
    except Exception:
        return False


def print_welcome():
    """Print welcome message."""
    console.print(
        Panel(
            "[bold cyan]goopenbot[/bold cyan] - AI-powered development tool\n"
            "[dim]Using local Ollama for AI inference[/dim]",
            border_style="cyan",
        )
    )
