import typer
import json
from pathlib import Path
from logging import getLogger
from rich.console import Console
from rich.markdown import Markdown
from alter.config import config
from alter.infrastructure.services.open_ai_service import OpenAIService
from .tools import TOOLS
from .prompts import SYSTEM_PROMPT

logger = getLogger(__name__)
console = Console()
app = typer.Typer(
    name=config.app_config.name, 
    help=f"{config.app_config.name} - {config.app_config.version}",
    no_args_is_help=True)

history = []
open_ai_service = OpenAIService()
@app.command()
def main():
    """Main command for the app."""
    typer.echo(f"{config.app_config.name} version {config.app_config.version}!")

@app.command()
def print_settings():
    """Print the current settings."""
    print(config)


def execute_tool(name: str, args: dict) -> str:
    try:
        if name == "read_file":
            return Path(args["path"]).read_text()
        elif name == "write_file":
            p = Path(args["path"])
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args["content"])
            return f"Written to {args['path']}"
        elif name == "list_files":
            p = Path(args.get("path", "."))
            return "\n".join(str(f) for f in p.iterdir())
    except Exception as e:
        return f"Error: {e}"

@app.command()
def repl(model: str = typer.Option(config.open_ai_config.model, "-m")):
    """Interactive REPL loop with file tools."""
    service = OpenAIService()
    history = [{"role": "system", "content": SYSTEM_PROMPT}]  # ← ici

    while True:
        try:
            user_input = typer.prompt("You")
            history.append({"role": "user", "content": user_input})

            # Agentic loop — keep going until no more tool calls
            while True:
                response = service.create_chat_completion(
                    model=model,
                    messages=history,
                    tools=TOOLS,
                )
                message = response["choices"][0]["message"]
                finish_reason = response["choices"][0]["finish_reason"]

                if finish_reason == "tool_calls":
                    history.append(message)  # append assistant's tool call request

                    for tool_call in message["tool_calls"]:
                        name = tool_call["function"]["name"]
                        args = json.loads(tool_call["function"]["arguments"])

                        console.print(f"[dim]⚙ {name}({args})[/dim]")
                        result = execute_tool(name, args)

                        history.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": result,
                        })
                else:
                    # No more tool calls — print final reply and break inner loop
                    reply = message["content"]
                    history.append({"role": "assistant", "content": reply})
                    console.print(Markdown(reply))
                    break

        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Bye![/dim]")
            raise typer.Exit()
