"""CLI interface for AI Security Capability Monitor."""

from __future__ import annotations

import json

import click
from rich.console import Console
from rich.table import Table

from .evaluator import EvaluationRunner
from .research import ResearchTracker
from .taxonomy import get_categories, get_taxonomy

console = Console()


@click.group()
def main():
    """AI Security Capability Monitor — track AI offensive security capabilities."""
    pass


@main.command()
@click.option("--model", required=True, help="Model ID to evaluate (e.g. gpt-4o)")
@click.option("--category", required=True, type=click.Choice(get_categories()), help="Capability category")
@click.option("--json-output", is_flag=True, help="Output as JSON")
def evaluate(model: str, category: str, json_output: bool):
    """Run benchmarks against a model for a capability category."""
    runner = EvaluationRunner()
    result = runner.evaluate(model, category)

    if json_output:
        click.echo(json.dumps(result, indent=2))
        return

    console.print(f"\n[bold]Model:[/bold] {result['model_id']}")
    console.print(f"[bold]Category:[/bold] {result['category']}")
    console.print(f"[bold]Overall Tier:[/bold] [red bold]{result['overall_tier']}[/red bold]")
    console.print(f"[bold]Avg Score:[/bold] {result['avg_score']}")

    table = Table(title="Benchmark Results")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Score", justify="right")
    table.add_column("Tier")
    table.add_column("Expected")
    for r in result.get("results", []):
        table.add_row(r["benchmark_id"], r["name"], f"{r['score']:.2f}", r["tier"], r["expected_tier"])
    console.print(table)


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind")
@click.option("--port", default=8150, type=int, help="Port")
def dashboard(host: str, port: int):
    """Launch the monitoring dashboard."""
    import uvicorn
    console.print(f"[bold green]Starting dashboard at http://{host}:{port}[/bold green]")
    uvicorn.run("aiscm.dashboard:app", host=host, port=port, reload=False)


@main.command(name="track-research")
@click.option("--max-results", default=20, type=int, help="Max papers to fetch")
def track_research(max_results: int):
    """Fetch and track recent AI security research from arXiv."""
    tracker = ResearchTracker()
    papers = tracker.fetch_arxiv(max_results=max_results)

    if not papers:
        console.print("[yellow]No papers found or API error.[/yellow]")
        return

    table = Table(title=f"Tracked {len(papers)} Papers")
    table.add_column("arXiv ID")
    table.add_column("Title", max_width=80)
    table.add_column("Relevance", justify="right")
    for p in papers:
        table.add_row(p["arxiv_id"], p["title"][:80], f"{p['relevance']:.1f}")
    console.print(table)


@main.command()
def taxonomy():
    """Display the capability taxonomy."""
    tax = get_taxonomy()
    for cat_name, cat_data in tax["categories"].items():
        console.print(f"\n[bold cyan]{cat_name}[/bold cyan]: {cat_data['description']}")
        table = Table()
        table.add_column("Tier")
        table.add_column("Name")
        table.add_column("Threshold", justify="right")
        table.add_column("Description")
        for tier_name, tier_data in cat_data["tiers"].items():
            table.add_row(tier_name, tier_data["name"], f"{tier_data['threshold_score']:.1f}", tier_data["description"])
        console.print(table)


@main.command()
def alerts():
    """Show recent alerts."""
    from .db import get_connection, get_alerts
    conn = get_connection()
    alert_list = get_alerts(conn)
    if not alert_list:
        console.print("[green]No alerts.[/green]")
        return
    for a in alert_list[:20]:
        icon = "🚨" if "UPGRADED" in a["message"] else "📉"
        console.print(f"{icon} [{a['created_at'][:16]}] {a['message']}")
