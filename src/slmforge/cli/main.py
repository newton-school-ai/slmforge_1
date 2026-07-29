"""SLMForge CLI entrypoint.

Subcommands are stubbed for M1. Real implementations land in M7.
"""

from __future__ import annotations

import json
import urllib.request

from typing import Any

import typer

_VALID_TASK_TYPES = frozenset(
    {
        "classification",
        "summarisation",
        "qa",
        "instruction",
        "chat",
        "auto",
    }
)

_VALID_TEMPLATES = frozenset({"phi3", "llama3.1"})

_API_BASE = "http://localhost:8000"

app = typer.Typer(no_args_is_help=True, help="SLMForge -- plug-and-play SLM builder.")

data_app = typer.Typer(no_args_is_help=True, help="Data management utilities.")
app.add_typer(data_app, name="data")


def _validate_override(value: str | None, valid_set: frozenset, flag: str, label: str) -> None:
    if value is not None and value not in valid_set:
        typer.echo(
            f"Error: invalid {label} '{value}' for --{flag}. "
            f"Must be one of: {', '.join(sorted(valid_set))}",
            err=True,
        )
        raise typer.Exit(code=1)


def _validate_base_model(value: str | None) -> None:
    if value is not None and value != "auto":
        from slmforge.finetune.registry import is_registered, list_models

        if not is_registered(value):
            valid = ", ".join(m.huggingface_id for m in list_models())
            typer.echo(
                f"Error: invalid base model '{value}' for --base. "
                f"Must be 'auto' or one of: {valid}",
                err=True,
            )
            raise typer.Exit(code=1)


def _build_payload(
    task: str | None,
    base: str | None,
    template: str | None,
    recipe: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "task_type": task or "auto",
        "base_model": base or "auto",
        "template": template or "phi3",
        "lora": {"r": 16, "alpha": 32, "dropout": 0.05},
        "training": {"epochs": 2, "batch_size": 16, "lr": 0.0002},
        "eval": {"llm_judge": False},
    }
    if recipe:
        payload["recipe"] = recipe
    if task:
        payload["_override_task"] = True
    if base:
        payload["_override_base"] = True
    if template:
        payload["_override_template"] = True
    return payload


def _post_build(payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{_API_BASE}/builds",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        typer.echo(f"API error ({e.code}): {body}", err=True)
        raise typer.Exit(code=1)
    except urllib.error.URLError:
        typer.echo(
            f"Error: could not reach the SLMForge API at {_API_BASE}. "
            f"Is the server running? (try `slmforge ui`)",
            err=True,
        )
        raise typer.Exit(code=1)


def _display_build(result: dict[str, Any]) -> None:
    typer.echo("Build created:")
    typer.echo(f"  ID:          {result.get('build_id', '?')}")
    typer.echo(f"  Task type:   {result.get('task_type', '?')}")
    typer.echo(f"  Base model:  {result.get('base_model', '?')}")
    typer.echo(f"  Template:    {result.get('template', '?')}")
    typer.echo(f"  Status:      {result.get('status', '?')}")


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
    auto: bool = typer.Option(False, "--auto", help="Skip all confirmation prompts."),
    recipe: str | None = typer.Option(None, "--recipe", help="Run a bundled recipe by name."),
    task: str | None = typer.Option(
        None,
        "--task",
        help="Override task type: classification, summarisation, qa, instruction, chat, or 'auto'.",
    ),
    base: str | None = typer.Option(
        None,
        "--base",
        help='Override base model: "auto" or HF model ID (e.g. microsoft/Phi-3-mini-4k-instruct).',
    ),
    template: str | None = typer.Option(
        None,
        "--template",
        help="Override chat template format: phi3 or llama3.1.",
    ),
) -> None:
    """Discover data in cwd, detect task, fine-tune, eval, and print usage doc."""
    _validate_override(task, _VALID_TASK_TYPES, "task", "task type")
    _validate_base_model(base)
    _validate_override(template, _VALID_TEMPLATES, "template", "template format")

    payload = _build_payload(task, base, template, recipe)
    try:
        result = _post_build(payload)
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    _display_build(result)


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
