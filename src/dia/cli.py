"""CLI entrypoint for dia."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="dia",
    help="Databricks Industry Accelerators — scaffold Databricks solutions in seconds.",
    add_completion=False,
)
console = Console()


@app.command()
def init(
    accelerator: str = typer.Argument(..., help="Accelerator to scaffold, e.g. 'medallion-sdp'"),
    industry: str = typer.Option(..., "--industry", "-i", help="Industry variant, e.g. 'finance'"),
    output: Path = typer.Option(Path("."), "--output", "-o", help="Parent directory for the generated project"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print what would be generated without writing"),
) -> None:
    """Initialize a new accelerator project in the current directory."""
    from dia.accelerators import get_accelerator
    from dia.industries import get_industry_config

    accelerator_cls = get_accelerator(accelerator)
    if accelerator_cls is None:
        console.print(
            f"[red]Unknown accelerator: {accelerator!r}. Run 'dia list' to see available accelerators.[/red]"
        )
        raise typer.Exit(code=1)

    industry_config = get_industry_config(accelerator, industry)
    if industry_config is None:
        console.print(
            f"[red]Industry {industry!r} is not supported for {accelerator!r}. "
            f"Run 'dia list' to see supported combinations.[/red]"
        )
        raise typer.Exit(code=1)

    acc = accelerator_cls(industry=industry, industry_config=industry_config)
    project_dir = output / acc.project_slug

    if project_dir.exists() and not force and any(project_dir.iterdir()):
        console.print(
            f"[red]Directory {project_dir} already exists and is not empty. Use --force to overwrite.[/red]"
        )
        raise typer.Exit(code=1)

    if dry_run:
        console.print(f"[yellow][dry-run] Would scaffold {accelerator!r} ({industry}) → {project_dir}[/yellow]")
        for path in acc.list_files():
            console.print(f"  [dim]{path}[/dim]")
        return

    console.print(f"Scaffolding [bold]{accelerator}[/bold] ({industry}) → [cyan]{project_dir}[/cyan]")
    acc.scaffold(target=project_dir, force=force)

    console.print(f"\n[green]✓[/green] Project ready at [cyan]{project_dir}[/cyan]\n")
    console.print("Next steps:")
    console.print(f"  [bold]cd {project_dir}[/bold]")
    console.print("  [bold]databricks bundle deploy --target dev[/bold]")


@app.command("list")
def list_resources(
    resource: str = typer.Argument("all", help="What to list: all | accelerators | industries"),
) -> None:
    """List available accelerators and industry combinations."""
    from dia.accelerators import ACCELERATOR_REGISTRY
    from dia.industries import list_industry_support

    if resource in ("all", "accelerators"):
        table = Table(title="Accelerators", show_header=True, header_style="bold cyan")
        table.add_column("Name", style="bold")
        table.add_column("Description")
        for name, cls in ACCELERATOR_REGISTRY.items():
            table.add_row(name, cls.description)
        console.print(table)

    if resource in ("all", "industries"):
        support = list_industry_support()
        accelerator_names = list(ACCELERATOR_REGISTRY.keys())
        table = Table(title="Industry × Accelerator Support", show_header=True, header_style="bold cyan")
        table.add_column("Industry", style="bold")
        for acc_name in accelerator_names:
            table.add_column(acc_name, justify="center")
        for industry_name, supported in sorted(support.items()):
            row = [industry_name] + ["[green]✓[/green]" if supported.get(a) else "[dim]—[/dim]" for a in accelerator_names]
            table.add_row(*row)
        console.print(table)


@app.command()
def deploy(
    env: str = typer.Option("dev", "--env", "-e", help="Target environment: dev | staging | prod"),
    project_dir: Path = typer.Option(Path("."), "--dir", "-d", help="Project directory (must contain databricks.yml)"),
) -> None:
    """Deploy the project via Databricks Asset Bundle."""
    from dia.deploy.bundle import deploy as _deploy

    if not (project_dir / "databricks.yml").exists():
        console.print(
            f"[red]No databricks.yml found in {project_dir}. Run 'dia init' first.[/red]"
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
