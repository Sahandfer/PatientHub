import sys
import importlib
import typer

COMMANDS = {
    "simulate": "Run a patient simulation session.",
    "create": "Create a new patient simulation implementation.",
    "generate": "Generate patient character profiles.",
    "evaluate": "Evaluate a simulated conversation or character profile.",
}
CONTEXT = {"allow_extra_args": True, "ignore_unknown_options": True}
app = typer.Typer()


def make_command(name: str, help: str):
    def command(ctx: typer.Context):
        sys.argv = [sys.argv[0]] + ctx.args
        module = importlib.import_module(f"patienthub.cli.{name}")
        getattr(module, name)()

    command.__name__ = name
    app.command(help=help, context_settings=CONTEXT)(command)


for cmd, desc in COMMANDS.items():
    make_command(cmd, desc)


if __name__ == "__main__":
    app()
