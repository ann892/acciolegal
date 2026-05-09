"""
Firm profile — single source of truth for branding across the dashboard,
proposal HTML, and engagement letter.

Loading order:
  1. FIRM_PROFILE_JSON env var (full profile as JSON string) — wins if set
  2. FIRM_PROFILE_FILE env var (path to a JSON file with the full profile)
  3. Individual FIRM_* scalar overrides (FIRM_NAME, FIRM_FOUNDER, etc.)
  4. Built-in fictional defaults (Verita Corporate Counsel)

This lets the same codebase serve multiple firms from different deploys
just by setting an env var per Render service:
  • Real firm (e.g. Komal/Accio): set FIRM_PROFILE_JSON to her full profile
  • Public fictional demo: leave env vars unset, defaults apply
"""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).parent

# -----------------------------------------------------------------------------
# Default fictional profile — used by the public demo deploy
# -----------------------------------------------------------------------------

DEFAULT_FIRM = {
    "name":           "Verita Corporate Counsel",
    "short":          "Verita",
    "mark":           "VC",
    "tagline":        "Matter Pipeline",
    "founder_name":   "Anjali Mehta",
    "founder_role":   "Managing Partner",
    "email":          "anjali@veritacounsel.com",
    "support_email":  "hello@veritacounsel.com",
    "phone":          "+91 80 4022 1100",
    "phone_alt":      "+91 80 4022 1101",
    "address":        "Level 4, Prestige Polygon, Anna Salai, Chennai 600035, India",
    "team": [
        {"initials": "AM", "name": "Anjali Mehta",       "role": "Managing Partner"},
        {"initials": "RK", "name": "Rajat Kapoor",       "role": "Senior Counsel"},
        {"initials": "PN", "name": "Priya Nair",         "role": "Senior Associate"},
        {"initials": "VS", "name": "Vikram Sundaram",    "role": "Senior Associate"},
        {"initials": "SI", "name": "Sneha Iyer",         "role": "Associate"},
        {"initials": "AB", "name": "Arjun Bhatt",        "role": "Associate"},
    ],
    "testimonials": [
        {
            "quote": "We needed our cap table investor-ready in three weeks before our Series A. Verita ran the regularization, restructured the buyback, and produced a diligence-ready package on time. The execution was crisp and the strategic counsel was sharper than what we'd received from larger firms at three times the cost.",
            "name": "Founder & CEO",
            "org": "Series A SaaS startup",
        },
        {
            "quote": "Anjali walked us through ESOP design with the kind of clarity I usually only see in textbooks. The vesting model she structured held up under VC scrutiny without a single change.",
            "name": "Co-Founder",
            "org": "Bangalore consumer tech",
        },
        {
            "quote": "Trademark filings done in five working days, exactly as quoted, with the right strategic advice on which classes to file across. No surprises on cost.",
            "name": "General Counsel",
            "org": "Healthtech, Series B",
        },
        {
            "quote": "Verita handled the legal piece of our cross-border SPA cleanly. Pricing was transparent up front, deliverables matched the proposal, no scope creep.",
            "name": "Co-Founder",
            "org": "B2B fintech, recent acquirer",
        },
    ],
    "notable_clients": [
        "Northwind Bioworks", "Aspire Robotics", "Lumio Health",
        "Padmaja Industries", "Calyx Capital", "Kestrel Studios",
        "Vyana Therapeutics", "Halcyon Pictures", "Indra Cloud",
        "Saanvi Foods", "Marigold Mobility", "Ashok & Sons",
        "Beacon Aerospace", "Chitra Materials", "Devyani Impact",
        "… and more",
    ],
}


# -----------------------------------------------------------------------------
# Loader
# -----------------------------------------------------------------------------

def _load_firm() -> dict:
    """Resolve the firm profile from env, file, or defaults."""

    # Highest priority: full profile as JSON string in env var
    profile_json = os.environ.get("FIRM_PROFILE_JSON")
    if profile_json:
        try:
            return json.loads(profile_json)
        except Exception as e:
            print(f"[firm_profile] FIRM_PROFILE_JSON failed to parse: {e}; falling back")

    # Next: profile from a file path
    profile_file = os.environ.get("FIRM_PROFILE_FILE")
    if profile_file:
        try:
            return json.loads(Path(profile_file).read_text())
        except Exception as e:
            print(f"[firm_profile] FIRM_PROFILE_FILE failed to load: {e}; falling back")

    # Otherwise: defaults, with optional individual scalar overrides
    profile = dict(DEFAULT_FIRM)
    overrides = {
        "name":          os.environ.get("FIRM_NAME"),
        "short":         os.environ.get("FIRM_SHORT"),
        "mark":          os.environ.get("FIRM_MARK"),
        "tagline":       os.environ.get("FIRM_TAGLINE"),
        "founder_name":  os.environ.get("FIRM_FOUNDER"),
        "founder_role":  os.environ.get("FIRM_FOUNDER_ROLE"),
        "email":         os.environ.get("FIRM_EMAIL"),
        "support_email": os.environ.get("FIRM_SUPPORT_EMAIL"),
        "phone":         os.environ.get("FIRM_PHONE"),
        "phone_alt":     os.environ.get("FIRM_PHONE_ALT"),
        "address":       os.environ.get("FIRM_ADDRESS"),
    }
    for k, v in overrides.items():
        if v is not None:
            profile[k] = v
    return profile


FIRM = _load_firm()
