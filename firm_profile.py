"""
Firm profile — single source of truth for branding across the dashboard,
proposal HTML, and engagement letter.

For the public demo (sharable with prospects, posts, etc.) we use a
fictional firm profile so we don't need permission from the real pilot
client. To switch to a real firm profile (e.g., for a private deployment
that creates drafts in that firm's actual Gmail), override the values
below or read from environment variables.
"""

from __future__ import annotations
import os

# Public demo defaults — fictional Indian corporate law firm.
# Believable but does not match any real firm.
FIRM = {
    "name":           os.environ.get("FIRM_NAME",        "Verita Corporate Counsel"),
    "short":          os.environ.get("FIRM_SHORT",       "Verita"),
    "mark":           os.environ.get("FIRM_MARK",        "VC"),    # 2-letter logo
    "tagline":        os.environ.get("FIRM_TAGLINE",     "Matter Pipeline"),
    "founder_name":   os.environ.get("FIRM_FOUNDER",     "Anjali Mehta"),
    "founder_role":   os.environ.get("FIRM_FOUNDER_ROLE","Managing Partner"),
    "email":          os.environ.get("FIRM_EMAIL",       "anjali@veritacounsel.com"),
    "support_email":  os.environ.get("FIRM_SUPPORT_EMAIL","hello@veritacounsel.com"),
    "phone":          os.environ.get("FIRM_PHONE",       "+91 80 4022 1100"),
    "phone_alt":      os.environ.get("FIRM_PHONE_ALT",   "+91 80 4022 1101"),
    "address":        os.environ.get("FIRM_ADDRESS",     "Level 4, Prestige Polygon, Anna Salai, Chennai 600035, India"),
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
        # All fictional — generic enough to look like real but match no real firm
        "Northwind Bioworks", "Aspire Robotics", "Lumio Health",
        "Padmaja Industries", "Calyx Capital", "Kestrel Studios",
        "Vyana Therapeutics", "Halcyon Pictures", "Indra Cloud",
        "Saanvi Foods", "Marigold Mobility", "Ashok & Sons",
        "Beacon Aerospace", "Chitra Materials", "Devyani Impact",
        "… and more",
    ],
}
