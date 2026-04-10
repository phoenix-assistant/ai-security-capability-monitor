"""FastAPI dashboard for AI Security Capability Monitor."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from .db import get_connection, get_latest_snapshots, get_alerts, get_papers
from .taxonomy import get_categories, get_taxonomy

app = FastAPI(title="AI Security Capability Monitor", version="0.1.0")


def _render_matrix(snapshots: list[dict]) -> str:
    """Build HTML capability matrix table."""
    categories = get_categories()
    models: dict[str, dict[str, str]] = {}
    for s in snapshots:
        models.setdefault(s["model_id"], {})[s["category"]] = s["tier"]

    tier_colors = {"L1": "#4caf50", "L2": "#8bc34a", "L3": "#ffc107", "L4": "#ff9800", "L5": "#f44336"}

    header = "<tr><th>Model</th>" + "".join(f"<th>{c}</th>" for c in categories) + "</tr>"
    rows = ""
    for model_id, cats in sorted(models.items()):
        cells = ""
        for c in categories:
            tier = cats.get(c, "—")
            color = tier_colors.get(tier, "#999")
            cells += f'<td style="background:{color};color:#fff;font-weight:bold;text-align:center">{tier}</td>'
        rows += f"<tr><td><strong>{model_id}</strong></td>{cells}</tr>"

    return f"<table border='1' cellpadding='8' cellspacing='0' style='border-collapse:collapse'>{header}{rows}</table>"


def _render_alerts(alerts: list[dict]) -> str:
    if not alerts:
        return "<p>No alerts.</p>"
    items = ""
    for a in alerts[:20]:
        icon = "🚨" if "UPGRADED" in a["message"] else "📉"
        items += f"<li>{icon} <strong>{a['created_at'][:16]}</strong> — {a['message']}</li>"
    return f"<ul>{items}</ul>"


def _render_papers(papers: list[dict]) -> str:
    if not papers:
        return "<p>No papers tracked yet. Run <code>aiscm track-research</code>.</p>"
    items = ""
    for p in papers[:15]:
        items += f"<li><strong>{p['title'][:100]}</strong> (relevance: {p.get('relevance_score', 0):.1f}) — <a href='https://arxiv.org/abs/{p['arxiv_id']}'>arXiv</a></li>"
    return f"<ul>{items}</ul>"


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    conn = get_connection()
    snapshots = get_latest_snapshots(conn)
    alerts = get_alerts(conn, unacknowledged_only=False)
    papers = get_papers(conn, limit=15)

    matrix_html = _render_matrix(snapshots)
    alerts_html = _render_alerts(alerts)
    papers_html = _render_papers(papers)

    return f"""<!DOCTYPE html>
<html><head><title>AISCM Dashboard</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #1a1a2e; color: #eee; }}
h1 {{ color: #e94560; }} h2 {{ color: #0f3460; background: #16213e; padding: 10px; border-radius: 4px; color: #eee; }}
table {{ width: 100%; margin: 20px 0; }} th {{ background: #16213e; padding: 10px; }} td {{ padding: 8px; }}
a {{ color: #e94560; }} ul {{ line-height: 1.8; }}
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
</style></head><body>
<h1>🛡️ AI Security Capability Monitor</h1>
<h2>Capability Matrix</h2>
{matrix_html if snapshots else "<p>No evaluations yet. Run <code>aiscm evaluate --model MODEL --category CATEGORY</code></p>"}
<div class="grid">
<div><h2>🚨 Alerts</h2>{alerts_html}</div>
<div><h2>📄 Research Papers</h2>{papers_html}</div>
</div>
</body></html>"""


@app.get("/api/snapshots")
async def api_snapshots():
    conn = get_connection()
    return get_latest_snapshots(conn)


@app.get("/api/alerts")
async def api_alerts():
    conn = get_connection()
    return get_alerts(conn)
