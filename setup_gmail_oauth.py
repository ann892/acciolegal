"""
One-time OAuth setup for Komal's Gmail.

Prereq (5 min):
  1. Go to console.cloud.google.com → create a new project ("Accio Legal Pilot")
  2. APIs & Services → Library → enable: Gmail API, Google Drive API
  3. APIs & Services → OAuth consent screen → External → fill in app name + support email
     → Add scopes: gmail.compose, gmail.readonly, drive.readonly
     → Add komal@acciolegal.com as a Test User
  4. Credentials → Create Credentials → OAuth client ID → Desktop app
     → Download JSON, save as `secrets/credentials.json` next to this script
  5. Run: python3 setup_gmail_oauth.py

A browser window opens. Komal logs in with komal@acciolegal.com, clicks
"Continue" past the unverified-app warning (expected for a test app), and
grants the requested permissions. A `secrets/token.json` is written.

That token is reusable forever (refresh tokens auto-renew). Re-run only if
you change scopes or revoke access.
"""

from __future__ import annotations

import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

ROOT = Path(__file__).parent
SECRETS_DIR = ROOT / "secrets"
CREDENTIALS_PATH = SECRETS_DIR / "credentials.json"
TOKEN_PATH = SECRETS_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def main() -> None:
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)

    if not CREDENTIALS_PATH.exists():
        sys.exit(
            f"\nMissing OAuth client credentials at:\n  {CREDENTIALS_PATH}\n\n"
            f"Follow the 5-step prereq in the docstring of this file to create\n"
            f"a Google Cloud project and download the OAuth client JSON.\n"
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
    creds = flow.run_local_server(
        port=0,
        prompt="consent",
        access_type="offline",
        authorization_prompt_message=(
            "\n→ A browser window will open. Sign in with komal@acciolegal.com, "
            "click through the unverified-app warning, and grant access.\n"
        ),
        success_message=(
            "Authentication successful. You can close this tab and return to the terminal."
        ),
    )

    TOKEN_PATH.write_text(creds.to_json())
    print(f"\n✓ Token saved to {TOKEN_PATH}")
    print(f"  Scopes granted: {', '.join(SCOPES)}")
    print(f"\nYou can now run the pipeline with --gmail-draft:")
    print(f"  python3 run_demo.py --mock --gmail-draft")


if __name__ == "__main__":
    main()
