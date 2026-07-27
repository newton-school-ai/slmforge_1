"""SLMForge CLI entrypoint.

Subcommands are stubbed for M1. Real implementations land in M7.
"""

from __future__ import annotations

import typer

from slmforge.api.schemas import TaskType, TemplateType

app = typer.Typer(no_args_is_help=True, help="SLMForge -- plug-and-play SLM builder.")

data_app = typer.Typer(no_args_is_help=True, help="Data management utilities.")
app.add_typer(data_app, name="data")


@data_app.command(name="prefetch")
def prefetch_cmd(
    dataset_id: str = typer.Argument(..., help="HuggingFace dataset ID."),
    split: str = typer.Option("train", "--split", help="Dataset split to prefetch."),
) -> None:
    """Prefetch a public HuggingFace dataset and cache it locally."""
    from slmforge.data.prefetch import CACHE_DIR, prefetch

    try:
        path = prefetch(dataset_id=dataset_id, split=split, cache_dir=CACHE_DIR)
        typer.echo(f"Cached at: {path}")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def init() -> None:
    """Initialise a .slmforge/ config directory in the current folder."""
    typer.echo("init: not yet implemented (M7)")


@app.command()
def build(
    auto: bool = typer.Option(
        False,
        "--auto",
        help="Skip all confirmation prompts.",
    ),
    recipe: str | None = typer.Option(
        None,
        "--recipe",
        help="Run a bundled recipe by name.",
    ),
    task: TaskType = typer.Option(
        TaskType.auto,
        "--task",
        help="Override detected task type.",
    ),
    base: str = typer.Option(
        "auto",
        "--base",
        help="Override detected base model.",
    ),
    template: TemplateType = typer.Option(
        TemplateType.auto,
        "--template",
        help="Override detected chat template.",
    ),
) -> None:
    """Build an SLM from a recipe or local model."""
    typer.echo(
        "build: not yet implemented (M7). "
        f"auto={auto} "
        f"recipe={recipe} "
        f"task={task.value} "
        f"base={base} "
        f"template={template.value}"
    )

@app.command()
def eval(build_id: str) -> None:  # noqa: A002
    """Re-run eval on an existing build."""
    typer.echo(f"eval: not yet implemented (M7). build_id={build_id}")


@app.command()
def serve(build_id: str, port: int = 8000) -> None:
    """Start a local vLLM endpoint for a build."""
    typer.echo(f"serve: not yet implemented (M7). build_id={build_id} port={port}")


@app.command(name="list")
def list_cmd() -> None:
    """List all builds in this folder."""
    typer.echo("list: not yet implemented (M7)")


@app.command()
def usage(build_id: str) -> None:
    """Print the USAGE.md for a build."""
    typer.echo(f"usage: not yet implemented (M7). build_id={build_id}")


@app.command()
def ui() -> None:
    """Launch the localhost web UI."""
    typer.echo("ui: not yet implemented (M7)")


if __name__ == "__main__":
    app()
