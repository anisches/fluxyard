from ollama import Client
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from rich.rule import Rule
from rich import box

from config import Config
from tools import TOOLS, dispatch

console = Console()

SYSTEM_PROMPT = """
You are a cynic — physics, chemistry, quantum, all of it. Answer everything as a cynic would.

Tools you have:
- web_search     → search the web when the user needs current info or news
- switch_model   → call when the user says "switch to X", "use X model", "change model to X"
- set_config     → call when the user wants to store a key or setting, e.g.:
                   "set my ollama api key to sk-xxx"
                   "set ollama host to http://192.168.1.10:11434"

Never break character. Never explain the tools. Just use them silently.
"""


def _make_client(config: Config) -> Client:
    headers = {}
    if config.ollama_api_key:
        headers["Authorization"] = f"Bearer {config.ollama_api_key}"
    return Client(host=config.ollama_host, headers=headers)


def print_banner(config: Config):
    console.print(
        Panel.fit(
            f"[bold red]FLUXYARD[/bold red]  [dim]— the cynic is in[/dim]  "
            f"[dim]·  {config.model}  ·  {config.ollama_host}[/dim]",
            border_style="red",
            box=box.DOUBLE_EDGE,
        )
    )
    console.print("[dim]type [bold]exit[/bold] or [bold]quit[/bold] to leave[/dim]\n")


def _msg_to_dict(msg) -> dict:
    d = {"role": msg.role, "content": msg.content or ""}
    if getattr(msg, "tool_calls", None):
        d["tool_calls"] = [
            {"function": {"name": tc.function.name, "arguments": tc.function.arguments}}
            for tc in msg.tool_calls
        ]
    return d


def run_agent(messages: list, config: Config) -> str:
    """Run one agent turn; loops internally until no more tool calls."""
    while True:
        client = _make_client(config)

        with Live(
            Spinner("dots", text=Text(f" [{config.model}] thinking...", style="dim")),
            console=console,
            transient=True,
        ):
            response = client.chat(model=config.model, messages=messages, tools=TOOLS)

        msg = response.message
        messages.append(_msg_to_dict(msg))

        if not getattr(msg, "tool_calls", None):
            return msg.content or ""

        for tc in msg.tool_calls:
            name = tc.function.name
            args = tc.function.arguments

            console.print(f"[dim]  ↳ {name}({args})[/dim]")
            result = dispatch(name, args, config)

            if name == "switch_model":
                console.print(f"[yellow]  model → {config.model}[/yellow]")
            elif name == "set_config":
                console.print(f"[green]  saved {args['key']}[/green]")

            messages.append({"role": "tool", "content": result, "name": name})


def main():
    config = Config()
    print_banner(config)

    history = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = console.input("[bold cyan]You[/bold cyan] › ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]cynically departing...[/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            console.print("[dim]finally, someone who knows when to leave.[/dim]")
            break

        history.append({"role": "user", "content": user_input})
        reply = run_agent(history, config)
        history.append({"role": "assistant", "content": reply})

        console.print()
        console.print(
            Panel(
                Markdown(reply),
                title=f"[bold red]Cynic[/bold red] [dim]({config.model})[/dim]",
                border_style="red dim",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
        console.print(Rule(style="dim red"))
        console.print()


if __name__ == "__main__":
    main()
