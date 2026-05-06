"""
Render an Accio Legal proposal as styled HTML.

The HTML is the primary deliverable for v1 — it renders inline in the
dashboard preview and can be opened in a browser. From the browser, Komal
hits Cmd+P / Ctrl+P → Save as PDF for a print-quality PDF that closely
approximates a Gamma-style deck.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
TEMPLATE_DIR = ROOT / "templates" / "proposal_html"


def render_proposal_html(content: dict) -> str:
    """Return a complete, self-contained HTML document for the proposal."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("proposal.html.j2")
    css = (TEMPLATE_DIR / "proposal.css").read_text()

    return template.render(
        title=content.get("title", "Proposal"),
        opening_paragraph=content.get("opening_paragraph", ""),
        approach_bullets=content.get("approach_bullets", []),
        scope_section_title=content.get("scope_section_title", "Scope of Services"),
        scope_section_intro=content.get("scope_section_intro", ""),
        phases=content.get("phases", []),
        deliverables=content.get("deliverables", []),
        cost_table=content.get("cost_table", []),
        total_fee_inr=sum(
            (row.get("fee_inr") or 0) for row in content.get("cost_table", [])
        ) or None,
        exclusions_note=content.get("exclusions_note", ""),
        deferred_note=content.get("deferred_note", ""),
        next_steps=content.get("next_steps", []),
        css=css,
        generated_date=date.today().strftime("%d %B %Y"),
    )


def save_proposal_html(content: dict, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_proposal_html(content), encoding="utf-8")
    return out_path


def try_render_pdf(html: str, out_path: Path) -> Path | None:
    """Attempt to convert the proposal HTML to PDF via WeasyPrint.

    Returns the output path on success, or None if WeasyPrint is not
    available on the host (e.g., system libs missing on Render free tier).
    Lazy-imports so the rest of the module loads even if WeasyPrint can't
    be imported.
    """
    try:
        from weasyprint import HTML
    except Exception as e:
        print(f"[proposal_render] WeasyPrint unavailable: {type(e).__name__}: {e}")
        return None

    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        HTML(string=html).write_pdf(str(out_path))
        return out_path
    except Exception as e:
        print(f"[proposal_render] PDF render failed: {type(e).__name__}: {e}")
        return None
