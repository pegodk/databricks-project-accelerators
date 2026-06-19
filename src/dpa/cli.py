"""CLI entrypoint for dpa."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="dpa",
    help="Databricks Project Accelerators — scaffold Databricks solutions in seconds.",
    add_completion=False,
)
console = Console()


@app.command()
def init(
    accelerator: str = typer.Argument(..., help="Accelerator to scaffold, e.g. 'medallion-sdp'"),
    output: Path = typer.Option(Path("."), "--output", "-o", help="Parent directory for the generated project"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print what would be generated without writing"),
) -> None:
    """Initialize a new accelerator project."""
    from dpa.accelerators import get_accelerator

    accelerator_cls = get_accelerator(accelerator)
    if accelerator_cls is None:
        console.print(
            f"[red]Unknown accelerator: {accelerator!r}. Run 'dpa list' to see available accelerators.[/red]"
        )
        raise typer.Exit(code=1)

    acc = accelerator_cls()
    project_dir = output / acc.project_slug

    if project_dir.exists() and not force and any(project_dir.iterdir()):
        console.print(
            f"[red]Directory {project_dir} already exists and is not empty. Use --force to overwrite.[/red]"
        )
        raise typer.Exit(code=1)

    if dry_run:
        console.print(f"[yellow][dry-run] Would scaffold {accelerator!r} → {project_dir}[/yellow]")
        for path in acc.list_files():
            console.print(f"  [dim]{path}[/dim]")
        return

    console.print(f"Scaffolding [bold]{accelerator}[/bold] → [cyan]{project_dir}[/cyan]")
    acc.scaffold(target=project_dir, force=force)

    console.print(f"\n[green]✓[/green] Project ready at [cyan]{project_dir}[/cyan]\n")
    console.print("Next steps:")
    console.print(f"  [bold]cd {project_dir}[/bold]")
    console.print("  [bold]databricks bundle deploy --target dev[/bold]")


@app.command("list")
def list_accelerators() -> None:
    """List available accelerators."""
    from dpa.accelerators import ACCELERATOR_REGISTRY

    table = Table(title="Accelerators", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    for name, cls in ACCELERATOR_REGISTRY.items():
        table.add_row(name, cls.description)
    console.print(table)


@app.command()
def deploy(
    env: str = typer.Option("dev", "--env", "-e", help="Target environment: dev | staging | prod"),
    project_dir: Path = typer.Option(Path("."), "--dir", "-d", help="Project directory (must contain databricks.yml)"),
) -> None:
    """Deploy the project via Databricks Asset Bundle."""
    from dpa.deploy.bundle import deploy as _deploy

    if not (project_dir / "databricks.yml").exists():
        console.print(
            f"[red]No databricks.yml found in {project_dir}. Run 'dpa init' first.[/red]"
        )
        raise typer.Exit(code=1)

    console.print(f"Deploying to [bold]{env}[/bold]…")
    try:
        _deploy(target_dir=project_dir, env=env)
        console.print(f"[green]✓[/green] Deployed to {env}")
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
