"""
Accio Legal — Matter Pipeline Dashboard

Two-page Streamlit app:
  • Pipeline — status board for matters in flight
  • Run a Matter — interactive demo flow (transcript → proposal → EL)

Run: streamlit run dashboard.py
"""

from __future__ import annotations

import json
import time
from datetime import date, datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "dashboard_data.json"
OUTPUT_DIR = ROOT / "output"

ACCIO_NAVY = "#0E2A47"
ACCIO_GOLD = "#C8A24B"

STATUS_ORDER = [
    "Call Done",
    "Proposal Drafted",
    "Proposal Sent",
    "Accepted — EL Pending",
    "EL Drafted",
    "EL Sent",
    "Engaged",
    "Delivered",
]

STATUS_COLORS = {
    "Call Done":              ("#E8E8E8", "#5A5A5A"),
    "Proposal Drafted":       ("#FFF4D6", "#8A6D00"),
    "Proposal Sent":          ("#E1ECFF", "#1F4FA8"),
    "Accepted — EL Pending":  ("#D6F0E0", "#1A7A3D"),
    "EL Drafted":             ("#FFEFD6", "#A65D00"),
    "EL Sent":                ("#D6E8FF", "#0E2A47"),
    "Engaged":                ("#0E2A47", "#FFFFFF"),
    "Delivered":              ("#3A3A3A", "#FFFFFF"),
}

PIPELINE_STATES_ACTIVE = {
    "Call Done",
    "Proposal Drafted",
    "Proposal Sent",
    "Accepted — EL Pending",
    "EL Drafted",
    "EL Sent",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@st.cache_data(ttl=5)
def load_pipeline() -> dict:
    return json.loads(DATA_PATH.read_text())


def fmt_inr(amount) -> str:
    if amount is None:
        return "TBD"
    ns = str(int(amount))
    if len(ns) <= 3:
        return f"₹{ns}"
    last3 = ns[-3:]
    rest = ns[:-3]
    groups = []
    while len(rest) > 2:
        groups.append(rest[-2:])
        rest = rest[:-2]
    if rest:
        groups.append(rest)
    groups.reverse()
    return f"₹{','.join(groups)},{last3}"


def status_badge_html(status: str) -> str:
    bg, fg = STATUS_COLORS.get(status, ("#E8E8E8", "#3A3A3A"))
    return (
        f"<span style='background:{bg};color:{fg};padding:3px 10px;"
        f"border-radius:12px;font-size:12px;font-weight:600;"
        f"white-space:nowrap;'>{status}</span>"
    )


def render_top_bar(active: str) -> None:
    st.markdown(
        f"""
        <div style='display:flex;align-items:center;justify-content:space-between;
                    padding:12px 0 4px 0;border-bottom:2px solid {ACCIO_NAVY};
                    margin-bottom:24px;'>
            <div>
                <div style='font-size:28px;font-weight:800;color:{ACCIO_NAVY};
                            letter-spacing:0.5px;'>ACCIO LEGAL</div>
                <div style='font-size:13px;color:#6A6A6A;margin-top:-2px;'>
                    {active} &nbsp;·&nbsp; Komal Shah, Co-Founder &amp; CEO
                </div>
            </div>
            <div style='font-size:12px;color:#8A8A8A;text-align:right;'>
                {date.today().strftime('%A, %d %B %Y')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown("###")
    st.markdown(
        f"<div style='text-align:center;font-size:11px;color:#9A9A9A;"
        f"padding-top:24px;border-top:1px solid #E8E8E8;'>"
        f"Accio Legal · 16 Gyanendra Kanan, Howrah 711112 · "
        f"hello@acciolegal.com · +91 91671 25177"
        f"</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Page: Pipeline
# ---------------------------------------------------------------------------

def page_pipeline() -> None:
    render_top_bar("Matter Pipeline")
    data = load_pipeline()
    matters = data["matters"]

    today = date.today()
    this_month_count = sum(
        1 for m in matters
        if datetime.strptime(m["first_call_date"], "%Y-%m-%d").date().month == today.month
        and datetime.strptime(m["first_call_date"], "%Y-%m-%d").date().year == today.year
    )
    active_count = sum(1 for m in matters if m["status"] in PIPELINE_STATES_ACTIVE)
    engaged_count = sum(1 for m in matters if m["status"] == "Engaged")
    delivered_count = sum(1 for m in matters if m["status"] == "Delivered")
    committed = sum(
        (m.get("total_fee_inr") or 0) for m in matters
        if m["status"] in {"Engaged", "Delivered"}
    )
    pipeline_value = sum(
        (m.get("total_fee_inr") or 0) for m in matters
        if m["status"] in PIPELINE_STATES_ACTIVE
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Matters this month", this_month_count)
    with c2: st.metric("Active in pipeline", active_count, help=f"₹{pipeline_value:,} potential")
    with c3: st.metric("Engaged · Delivered", f"{engaged_count} · {delivered_count}")
    with c4: st.metric("Committed fees (engaged + delivered)", fmt_inr(committed))

    st.markdown("###")

    f1, f2, f3 = st.columns([2, 2, 1])
    with f1:
        status_filter = st.multiselect("Filter by status", options=STATUS_ORDER, default=[], placeholder="All statuses")
    with f2:
        owner_filter = st.multiselect("Filter by owner", options=sorted({m["owner"] for m in matters}), default=[], placeholder="All owners")
    with f3:
        sort_choice = st.selectbox("Sort by", ["First call (newest)", "First call (oldest)", "Fee (high → low)", "Status"])

    filtered = matters
    if status_filter: filtered = [m for m in filtered if m["status"] in status_filter]
    if owner_filter: filtered = [m for m in filtered if m["owner"] in owner_filter]

    if sort_choice == "First call (newest)":
        filtered = sorted(filtered, key=lambda x: x["first_call_date"], reverse=True)
    elif sort_choice == "First call (oldest)":
        filtered = sorted(filtered, key=lambda x: x["first_call_date"])
    elif sort_choice == "Fee (high → low)":
        filtered = sorted(filtered, key=lambda x: x.get("total_fee_inr") or 0, reverse=True)
    elif sort_choice == "Status":
        filtered = sorted(filtered, key=lambda x: STATUS_ORDER.index(x["status"]) if x["status"] in STATUS_ORDER else 99)

    st.markdown(
        f"<div style='font-size:14px;color:#6A6A6A;margin:12px 0 6px 0;'>"
        f"Showing {len(filtered)} of {len(matters)} matters</div>",
        unsafe_allow_html=True,
    )

    for m in filtered:
        fee_str = fmt_inr(m.get("total_fee_inr"))
        label = (
            f"{m['client_short']}  ·  {m['matter_type']}  ·  "
            f"{m['first_call_date']}  ·  {fee_str}  ·  Owner: {m['owner']}"
        )
        with st.expander(label, expanded=False):
            h1, h2 = st.columns([3, 1])
            with h1:
                st.markdown(
                    f"<div style='font-size:18px;font-weight:700;color:{ACCIO_NAVY};'>"
                    f"{m['client_name']}</div>"
                    f"<div style='font-size:13px;color:#6A6A6A;margin-top:2px;'>"
                    f"{m['id']}  ·  {m['matter_type']}</div>",
                    unsafe_allow_html=True,
                )
            with h2:
                st.markdown(
                    f"<div style='text-align:right;'>{status_badge_html(m['status'])}</div>",
                    unsafe_allow_html=True,
                )

            st.write("")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"**Primary contact**  \n{m['primary_contact']}  \n<{m['primary_email']}>")
            with m2:
                st.markdown(f"**First call**  \n{m['first_call_date']}  \n**Owner**: {m['owner']}")
            with m3:
                st.markdown(
                    f"**Total fee**  \n{fmt_inr(m.get('total_fee_inr'))}  \n"
                    f"_excl. govt fees, stamp duty, taxes_"
                )

            st.markdown("---")
            st.markdown("**Matter summary**")
            st.write(m["summary"])

            if m.get("deferred_note"):
                st.info(f"**Deferred / separate**: {m['deferred_note']}")

            if m.get("phases"):
                st.markdown("**Scope & pricing**")
                phase_table = [
                    {"Phase": p["name"], "TAT": p["tat"], "Fee": fmt_inr(p["fee_inr"])}
                    for p in m["phases"]
                ]
                st.dataframe(phase_table, hide_index=True, width="stretch")

            st.markdown(
                f"<div style='background:#FFF8E1;border-left:3px solid {ACCIO_GOLD};"
                f"padding:10px 14px;border-radius:4px;margin-top:8px;'>"
                f"<strong>Next action</strong> &nbsp;·&nbsp; {m['next_action']}"
                f"</div>",
                unsafe_allow_html=True,
            )

            docs_present = []
            if m.get("proposal_path"):
                p = ROOT / m["proposal_path"]
                if p.exists():
                    docs_present.append(("Proposal (.docx)", p))
            if m.get("el_path"):
                p = ROOT / m["el_path"]
                if p.exists():
                    docs_present.append(("Engagement letter (.docx)", p))

            if docs_present:
                st.markdown("---")
                st.markdown("**Documents**")
                cols = st.columns(len(docs_present))
                for col, (label, path) in zip(cols, docs_present):
                    with col:
                        with open(path, "rb") as f:
                            st.download_button(
                                label=f"⬇  {label}",
                                data=f.read(),
                                file_name=path.name,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"dl_{m['id']}_{label}",
                                width="stretch",
                            )


# ---------------------------------------------------------------------------
# Page: Run a Matter (interactive demo)
# ---------------------------------------------------------------------------

def page_run_matter() -> None:
    from scenarios import SCENARIOS
    from proposal_render import render_proposal_html, save_proposal_html
    from run_demo import (
        render_proposal_docx,
        render_engagement_letter,
        EL_TEMPLATE_PATH,
    )

    render_top_bar("Run a Matter")

    st.markdown(
        f"<div style='background:#F8FAFC;border-left:3px solid {ACCIO_NAVY};"
        f"padding:14px 18px;border-radius:0 6px 6px 0;margin-bottom:24px;'>"
        f"<strong>How this works.</strong> Pick a sample first-call transcript below. "
        f"Click <em>Generate proposal</em> to see the AI extract scope and pricing, "
        f"draft a Komal-voice proposal, and render it inline. Then simulate the "
        f"client's acceptance and watch the engagement letter fill itself.</div>",
        unsafe_allow_html=True,
    )

    # ----- Step 1: pick scenario -----
    st.subheader("1. Pick a sample call")

    scenario_keys = list(SCENARIOS.keys())
    scenario_labels = [SCENARIOS[k]["label"] for k in scenario_keys]
    chosen_label = st.selectbox(
        "Sample first-call transcript",
        options=scenario_labels,
        index=0,
        label_visibility="collapsed",
    )
    chosen_key = scenario_keys[scenario_labels.index(chosen_label)]
    scenario = SCENARIOS[chosen_key]

    transcript_text = scenario["transcript_path"].read_text()
    reply_text = scenario["reply_path"].read_text()

    with st.expander("Read the transcript", expanded=False):
        st.text(transcript_text)

    # Reset state if scenario changes
    if st.session_state.get("active_scenario") != chosen_key:
        for k in ("matter_data", "proposal_content", "proposal_html",
                 "proposal_html_path", "proposal_docx_path",
                 "reply_data", "el_path"):
            st.session_state.pop(k, None)
        st.session_state["active_scenario"] = chosen_key

    # ----- Step 2: generate proposal -----
    st.subheader("2. Generate proposal")

    if st.button("Generate proposal", type="primary", disabled=("proposal_content" in st.session_state)):
        mock_dir = scenario["mock_dir"]
        client_slug = scenario["client_slug"]

        with st.spinner("Reading transcript and extracting scope, pricing, client details..."):
            time.sleep(1.0)
            data = json.loads((mock_dir / "01_matter_data.json").read_text())
            st.session_state["matter_data"] = data

        with st.spinner("Drafting proposal in Komal's voice using prior-deal style references..."):
            time.sleep(1.0)
            content = json.loads((mock_dir / "02_proposal_narrative.json").read_text())
            st.session_state["proposal_content"] = content

        with st.spinner("Rendering proposal as branded HTML and Word fallback..."):
            time.sleep(0.6)
            html = render_proposal_html(content)
            html_path = OUTPUT_DIR / f"{client_slug}_Proposal.html"
            save_proposal_html(content, html_path)
            docx_path = OUTPUT_DIR / f"{client_slug}_Proposal.docx"
            render_proposal_docx(content, data, docx_path)
            st.session_state["proposal_html"] = html
            st.session_state["proposal_html_path"] = html_path
            st.session_state["proposal_docx_path"] = docx_path

        st.rerun()

    # Render the result if we have one
    if "matter_data" in st.session_state and "proposal_content" in st.session_state:
        data = st.session_state["matter_data"]
        client = data["client"]

        st.success("Proposal drafted. Review what was extracted and the proposal preview below.")

        # Extraction summary
        with st.container(border=True):
            st.markdown(
                f"<div style='font-size:11px;letter-spacing:1.5px;text-transform:uppercase;"
                f"color:{ACCIO_GOLD};font-weight:700;'>Extraction Checkpoint</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size:18px;font-weight:700;color:{ACCIO_NAVY};margin:4px 0 12px 0;'>"
                f"{client['legal_name']}</div>",
                unsafe_allow_html=True,
            )
            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown(f"**Entity**  \n{client.get('entity_type', '—')}")
                st.markdown(f"**Address**  \n{client.get('registered_address', '—')}")
            with cc2:
                st.markdown(f"**Primary contact**  \n{client.get('primary_contact_name', '—')}  \n<{client.get('primary_contact_email', '—')}>")
                st.markdown(f"**Signatory**  \n{client.get('signatory_name', '—')} ({client.get('signatory_designation', '—')})")

            st.markdown("**Matter summary**")
            st.write(data.get("matter_summary", ""))

            phases_table = [
                {
                    "Phase": p["name"],
                    "TAT": p.get("tat_days", ""),
                    "Fee (INR)": fmt_inr(p.get("fee_inr")),
                }
                for p in data.get("phases", [])
            ]
            st.dataframe(phases_table, hide_index=True, width="stretch")

            total = data.get("total_fee_inr")
            if total:
                st.markdown(
                    f"<div style='text-align:right;font-size:16px;font-weight:700;"
                    f"color:{ACCIO_NAVY};margin-top:4px;'>Total: {fmt_inr(total)}</div>",
                    unsafe_allow_html=True,
                )
            if data.get("deferred_or_separate"):
                st.info(f"**Deferred / separate**: {data['deferred_or_separate']}")

        st.markdown("###")
        st.markdown(
            f"<div style='font-size:11px;letter-spacing:1.5px;text-transform:uppercase;"
            f"color:{ACCIO_GOLD};font-weight:700;margin-bottom:6px;'>Proposal Preview</div>",
            unsafe_allow_html=True,
        )

        # Download buttons
        d1, d2, _ = st.columns([1, 1, 3])
        with d1:
            html_path = st.session_state["proposal_html_path"]
            with open(html_path, "rb") as f:
                st.download_button(
                    "⬇  Download HTML",
                    data=f.read(),
                    file_name=html_path.name,
                    mime="text/html",
                    width="stretch",
                )
        with d2:
            docx_path = st.session_state["proposal_docx_path"]
            with open(docx_path, "rb") as f:
                st.download_button(
                    "⬇  Download Word",
                    data=f.read(),
                    file_name=docx_path.name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    width="stretch",
                )

        st.caption("To save a PDF: download the HTML, open it in a browser, and use Cmd+P / Ctrl+P → Save as PDF.")

        # Inline HTML preview
        components.html(st.session_state["proposal_html"], height=1100, scrolling=True)

        # ----- Step 3: simulate reply + generate EL -----
        st.markdown("###")
        st.subheader("3. Simulate the client's response")

        with st.expander("Read the client's acceptance email", expanded=False):
            st.text(reply_text)

        if st.button("Generate engagement letter", type="primary", disabled=("el_path" in st.session_state)):
            mock_dir = scenario["mock_dir"]
            client_slug = scenario["client_slug"]

            with st.spinner("Classifying the client's reply..."):
                time.sleep(0.8)
                reply_data = json.loads((mock_dir / "03_reply_classification.json").read_text())
                st.session_state["reply_data"] = reply_data

            with st.spinner("Filling Komal's engagement letter template..."):
                time.sleep(0.8)
                el_path = OUTPUT_DIR / f"{client_slug}_Engagement_Letter.docx"
                render_engagement_letter(EL_TEMPLATE_PATH, data, reply_data, el_path)
                st.session_state["el_path"] = el_path

            st.rerun()

        if "el_path" in st.session_state:
            reply_data = st.session_state["reply_data"]
            st.success(
                f"Reply classified: **{reply_data['classification']}** — {reply_data['rationale']}"
            )

            if reply_data.get("client_questions"):
                st.warning(
                    "Client asked questions Komal should answer before sending the EL:\n\n"
                    + "\n".join(f"- {q}" for q in reply_data["client_questions"])
                )

            st.markdown(
                f"<div style='font-size:11px;letter-spacing:1.5px;text-transform:uppercase;"
                f"color:{ACCIO_GOLD};font-weight:700;margin-bottom:6px;'>Engagement Letter</div>",
                unsafe_allow_html=True,
            )

            el_path = st.session_state["el_path"]
            with open(el_path, "rb") as f:
                st.download_button(
                    f"⬇  Download {el_path.name}",
                    data=f.read(),
                    file_name=el_path.name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    width="stretch",
                )
            st.caption(
                "The engagement letter uses Komal's existing Word template — only the "
                "client party block, effective date, scope table, signatory, and address "
                "fields are filled in. The clauses are unchanged."
            )

    if st.button("Reset and start over"):
        for k in ("matter_data", "proposal_content", "proposal_html",
                 "proposal_html_path", "proposal_docx_path",
                 "reply_data", "el_path", "active_scenario"):
            st.session_state.pop(k, None)
        st.rerun()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="Accio Legal — Matter Pipeline",
        page_icon="⚖",
        layout="wide",
    )

    st.markdown(
        f"""
        <style>
        .block-container {{padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px;}}
        [data-testid="stMetricValue"] {{font-size: 26px; color: {ACCIO_NAVY};}}
        [data-testid="stMetricLabel"] {{font-size: 12px;}}
        details summary {{font-size: 14px; padding: 8px 0;}}
        section[data-testid="stSidebar"] {{background: #FAFBFC;}}
        section[data-testid="stSidebar"] h2 {{color: {ACCIO_NAVY};}}
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            f"<div style='font-size:20px;font-weight:800;color:{ACCIO_NAVY};"
            f"letter-spacing:1px;padding:8px 0 4px 0;'>ACCIO LEGAL</div>"
            f"<div style='font-size:11px;color:#8A8A8A;letter-spacing:1px;"
            f"text-transform:uppercase;margin-bottom:18px;'>Matter Operations</div>",
            unsafe_allow_html=True,
        )
        page = st.radio(
            "Navigate",
            ["Pipeline", "Run a Matter"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.caption(
            "Demo mode — no API calls, no Gmail integration. "
            "All outputs are pre-generated for the seeded scenarios."
        )

    if page == "Pipeline":
        page_pipeline()
    else:
        page_run_matter()

    render_footer()


if __name__ == "__main__":
    main()
