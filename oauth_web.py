"""
Web Application OAuth flow helpers.

Different from setup_gmail_oauth.py which uses the Desktop OAuth flow
(localhost callback, browser auto-opens). Here we use the Web Application
flow so Komal can grant consent by clicking a link from her email — no
co-located terminal required.

Flow:
  1. Dashboard generates the Google authorize URL → user clicks → signs in
  2. Google redirects back to the dashboard URL with ?code=... in query params
  3. Dashboard exchanges code for tokens and saves them
"""

from __future__ import annotations

import json
import secrets as _crypto_secrets
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

ROOT = Path(__file__).parent
SECRETS_DIR = ROOT / "secrets"
WEB_CREDENTIALS_PATH = SECRETS_DIR / "credentials_web.json"
TOKEN_PATH = SECRETS_DIR / "token.json"

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def load_web_client_config() -> dict:
    """Load the Web App OAuth client config.

    Order of preference:
      1. secrets/credentials_web.json on disk (local dev)
      2. st.secrets["GOOGLE_OAUTH_WEB_JSON"] (Streamlit Cloud / deployed)
    """
    if WEB_CREDENTIALS_PATH.exists():
        return json.loads(WEB_CREDENTIALS_PATH.read_text())

    try:
        import streamlit as st
        cfg_str = st.secrets.get("GOOGLE_OAUTH_WEB_JSON") if hasattr(st, "secrets") else None
        if cfg_str:
            return json.loads(cfg_str)
    except Exception:
        pass

    raise FileNotFoundError(
        f"Missing Web App OAuth credentials.\n"
        f"  Local: drop the JSON at {WEB_CREDENTIALS_PATH}\n"
        f"  Cloud: set GOOGLE_OAUTH_WEB_JSON in Streamlit Cloud → Settings → Secrets\n"
        f"  See GCP_WEB_OAUTH.md."
    )


def make_authorize_url(redirect_uri: str, state: str) -> str:
    """Generate the Google authorize URL.

    The user clicks this URL, signs in with their Google account, grants the
    requested scopes, and Google redirects them back to `redirect_uri` with
    a one-time auth code in the query string.
    """
    config = load_web_client_config()
    flow = Flow.from_client_config(config, scopes=GMAIL_SCOPES, redirect_uri=redirect_uri)
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
        state=state,
    )
    return auth_url


def exchange_code_for_token(redirect_uri: str, code: str) -> dict:
    """Exchange a one-time auth code for a long-lived token.

    Returns the credentials as a dict (token + refresh_token + scopes).
    Save this somewhere durable; the refresh_token is what lets the app
    keep making API calls on the user's behalf indefinitely.
    """
    config = load_web_client_config()
    flow = Flow.from_client_config(config, scopes=GMAIL_SCOPES, redirect_uri=redirect_uri)
    flow.fetch_token(code=code)
    creds = flow.credentials
    return json.loads(creds.to_json())


def save_token_locally(token_dict: dict) -> Path:
    """Persist the token as secrets/token.json (for local dev)."""
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(json.dumps(token_dict, indent=2))
    return TOKEN_PATH


def whoami(token_dict: dict) -> str | None:
    """Inspect a token to find the authenticated email, if available.

    Falls back to None if the token doesn't carry an `id_token` payload.
    """
    # The simplest path: introspect via the Gmail profile API.
    try:
        creds = Credentials.from_authorized_user_info(token_dict, GMAIL_SCOPES)
        from googleapiclient.discovery import build
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        return profile.get("emailAddress")
    except Exception:
        return None


def make_state() -> str:
    """Generate a CSRF state token for the OAuth flow."""
    return _crypto_secrets.token_urlsafe(32)
