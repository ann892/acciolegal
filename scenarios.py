"""
Sample scenarios available for the demo.

Each scenario bundles a sample transcript, a sample client reply, and
pre-generated mock outputs (matter_data, proposal_narrative, reply_classification).

Add a new matter type by:
1. Drop a transcript at samples/transcript_<key>.txt
2. Drop a reply at samples/reply_<key>.txt
3. Pre-generate the three mock JSONs under mock/<key>/
4. Add an entry below
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parent

SCENARIOS = {
    "velara": {
        "label": "Velara Bioworks — Cap Table Cleanup & ESOP",
        "matter_type": "Cap Table Cleanup & ESOP",
        "transcript_path": ROOT / "samples" / "transcript.txt",
        "reply_path": ROOT / "samples" / "client_reply.txt",
        "mock_dir": ROOT / "mock" / "velara",
        "client_slug": "Velara",
    },
    "niramai": {
        "label": "Niramai Health — Trademark Filing",
        "matter_type": "Trademark Filing",
        "transcript_path": ROOT / "samples" / "transcript_niramai.txt",
        "reply_path": ROOT / "samples" / "reply_niramai.txt",
        "mock_dir": ROOT / "mock" / "niramai",
        "client_slug": "Niramai",
    },
    "glyph": {
        "label": "Glyph Studios — Founders Agreement & ESOP",
        "matter_type": "Founders Agreement & ESOP",
        "transcript_path": ROOT / "samples" / "transcript_glyph.txt",
        "reply_path": ROOT / "samples" / "reply_glyph.txt",
        "mock_dir": ROOT / "mock" / "glyph",
        "client_slug": "Glyph",
    },
}


def get_scenario(key: str) -> dict:
    if key not in SCENARIOS:
        raise KeyError(f"Unknown scenario '{key}'. Available: {list(SCENARIOS)}")
    return SCENARIOS[key]
