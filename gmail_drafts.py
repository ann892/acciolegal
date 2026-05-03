"""
Gmail draft creation for the Accio Legal pipeline.

Creates a Gmail draft addressed to the client with the proposal or engagement
letter .docx attached. Komal opens her Drafts folder, scans, edits if needed,
and hits send.

Auth flow: see setup_gmail_oauth.py to generate token.json once.
"""

from __future__ import annotations

import base64
import mimetypes
from email.message import EmailMessage
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ROOT = Path(__file__).parent
TOKEN_PATH = ROOT / "secrets" / "token.json"

# Scopes needed:
#   gmail.compose: create drafts (does NOT auto-send — Komal still hits Send)
#   gmail.readonly: needed for the reply watcher in Stage 4
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def _load_credentials():
    """Load OAuth credentials from local file or Streamlit Cloud secrets.

    Order of preference:
      1. secrets/token.json on disk (local dev)
      2. st.secrets["GMAIL_TOKEN_JSON"] (Streamlit Cloud / deployed)
    """
    import json

    if TOKEN_PATH.exists():
        return Credentials.from_authorized_user_file(str(TOKEN_PATH), GMAIL_SCOPES)

    # Fallback: Streamlit Cloud secrets (only available when running under streamlit)
    try:
        import streamlit as st
        token_str = st.secrets.get("GMAIL_TOKEN_JSON") if hasattr(st, "secrets") else None
        if token_str:
            return Credentials.from_authorized_user_info(json.loads(token_str), GMAIL_SCOPES)
    except Exception:
        pass

    raise FileNotFoundError(
        "No Gmail OAuth token found. Either:\n"
        "  1. Run python3 setup_gmail_oauth.py to authenticate locally, or\n"
        "  2. Use the Connect Gmail button in the dashboard's Settings page, or\n"
        "  3. Set GMAIL_TOKEN_JSON in Streamlit Cloud secrets."
    )


def get_gmail_service():
    """Load saved OAuth credentials and return an authenticated Gmail service."""
    creds = _load_credentials()
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        if TOKEN_PATH.exists():
            TOKEN_PATH.write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def create_proposal_draft(
    *,
    to_email: str,
    to_name: str,
    client_legal_name: str,
    matter_summary: str,
    attachment_path: Path,
    sender_display: str = "Komal Shah <komal@acciolegal.com>",
) -> dict:
    """Create a Gmail draft with the proposal attached.

    Returns the draft metadata dict, including the draft ID and a deep link
    Komal can click to jump straight into the draft in Gmail web.
    """
    msg = EmailMessage()
    msg["To"] = f"{to_name} <{to_email}>"
    msg["From"] = sender_display
    msg["Subject"] = f"Proposal — {client_legal_name}"

    body = (
        f"Hi {to_name.split()[0]},\n\n"
        f"Thanks again for the call. Please find attached our proposal covering "
        f"{matter_summary[:120]}{'...' if len(matter_summary) > 120 else ''}\n\n"
        f"Happy to walk through any of it on a quick call. To proceed, a confirmation "
        f"of acceptance over email is sufficient and we'll send across the engagement "
        f"agreement straight after.\n\n"
        f"Best,\n"
        f"Komal Shah\n"
        f"Accio Legal\n"
        f"komal@acciolegal.com  |  +91 91671 25177\n"
    )
    msg.set_content(body)

    return _attach_and_create_draft(msg, attachment_path)


def create_engagement_letter_draft(
    *,
    to_email: str,
    to_name: str,
    client_legal_name: str,
    attachment_path: Path,
    kickoff_date: str | None = None,
    sender_display: str = "Komal Shah <komal@acciolegal.com>",
) -> dict:
    """Create a Gmail draft with the engagement letter attached."""
    msg = EmailMessage()
    msg["To"] = f"{to_name} <{to_email}>"
    msg["From"] = sender_display
    msg["Subject"] = f"Engagement Agreement — {client_legal_name}"

    kickoff_line = (
        f"As discussed, we'll commence the moment we receive the signed engagement "
        f"letter and the 50% advance"
        + (f" — kickoff date {kickoff_date}." if kickoff_date else ".")
    )
    body = (
        f"Hi {to_name.split()[0]},\n\n"
        f"Thanks for the confirmation. Please find attached the engagement agreement "
        f"for {client_legal_name}. Kindly review, sign, and return at your convenience.\n\n"
        f"{kickoff_line}\n\n"
        f"Bank details for the advance will follow under separate cover once the "
        f"engagement letter is countersigned.\n\n"
        f"Best,\n"
        f"Komal Shah\n"
        f"Accio Legal\n"
        f"komal@acciolegal.com  |  +91 91671 25177\n"
    )
    msg.set_content(body)

    return _attach_and_create_draft(msg, attachment_path)


def _attach_and_create_draft(msg: EmailMessage, attachment_path: Path) -> dict:
    """Attach the given file and create a Gmail draft."""
    if not attachment_path.exists():
        raise FileNotFoundError(f"Attachment not found: {attachment_path}")

    ctype, encoding = mimetypes.guess_type(str(attachment_path))
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)

    with open(attachment_path, "rb") as f:
        data = f.read()

    msg.add_attachment(
        data,
        maintype=maintype,
        subtype=subtype,
        filename=attachment_path.name,
    )

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    service = get_gmail_service()
    try:
        draft = service.users().drafts().create(
            userId="me",
            body={"message": {"raw": raw}},
        ).execute()
    except HttpError as e:
        raise RuntimeError(f"Gmail API error creating draft: {e}") from e

    draft_id = draft.get("id")
    message_id = draft.get("message", {}).get("id")
    return {
        "draft_id": draft_id,
        "message_id": message_id,
        "gmail_url": f"https://mail.google.com/mail/u/0/#drafts?compose={draft_id}",
        "subject": msg["Subject"],
        "to": msg["To"],
    }
