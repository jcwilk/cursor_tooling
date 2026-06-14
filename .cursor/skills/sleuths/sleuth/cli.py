from __future__ import annotations

import sys
from pathlib import Path

import click

from sleuth.refresh import refresh_all, refresh_sleuth
from sleuth.reset import reset_all, reset_sleuth
from sleuth.tracing import configure_langsmith, flush_tracing


@click.group()
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Project root (directory containing .sleuths/)",
)
@click.pass_context
def cli(ctx: click.Context, project_root: Path) -> None:
    ctx.ensure_object(dict)
    ctx.obj["project_root"] = project_root.resolve()
    configure_langsmith(ctx.obj["project_root"])


@cli.command()
@click.option("--sleuth", default=None, help="Sleuth id (matches .sleuths/queries/<id>.yaml)")
@click.option("--all", "refresh_all_flag", is_flag=True, help="Refresh every sleuth")
@click.pass_context
def refresh(ctx: click.Context, sleuth: str | None, refresh_all_flag: bool) -> None:
    """Incrementally refresh sleuth summaries."""
    root: Path = ctx.obj["project_root"]
    try:
        if refresh_all_flag:
            refresh_all(root)
        elif sleuth:
            refresh_sleuth(root, sleuth)
        else:
            raise click.ClickException("specify --sleuth <id> or --all")
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        flush_tracing()


@cli.command()
@click.option("--sleuth", default=None, help="Sleuth id (matches .sleuths/queries/<id>.yaml)")
@click.option("--all", "reset_all_flag", is_flag=True, help="Reset every sleuth")
@click.pass_context
def reset(ctx: click.Context, sleuth: str | None, reset_all_flag: bool) -> None:
    """Remove summary and checkpoint so the next refresh starts from scratch."""
    root: Path = ctx.obj["project_root"]
    try:
        if reset_all_flag:
            reset_all(root)
        elif sleuth:
            reset_sleuth(root, sleuth)
        else:
            raise click.ClickException("specify --sleuth <id> or --all")
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        flush_tracing()


def main() -> None:
    try:
        cli(obj={})
    except click.ClickException as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
