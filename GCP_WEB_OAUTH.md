# GCP — Web Application OAuth client (one-time, ~3 min)

We already have a Desktop OAuth client (used for `setup_gmail_oauth.py`). For the
in-dashboard "Connect Gmail" button to work — so Komal can authenticate by
clicking a link from her email — we need a **second** OAuth client, of type
"Web application", with a redirect URL pointing at the dashboard.

Don't delete the Desktop client. Both can coexist. Desktop is for local terminal
auth; Web is for Komal's browser-based one-click flow.

## Steps

### 1. Open your existing GCP project

[console.cloud.google.com](https://console.cloud.google.com) → make sure
"Accio Legal Pilot" is selected in the top dropdown.

### 2. Create a new OAuth client

1. Left sidebar: **APIs & Services → Credentials**
2. Top button: **+ CREATE CREDENTIALS → OAuth client ID**
3. **Application type**: **Web application**
4. **Name**: `Accio Legal Pilot Web`
5. **Authorized redirect URIs** — click **+ ADD URI** and add **both** of these:
   - `http://localhost:8501/`
   - `https://YOUR-STREAMLIT-SUBDOMAIN.streamlit.app/`
     (replace with your actual Streamlit Cloud URL once you've deployed; if
     you haven't deployed yet, just add the localhost one and add the
     production URL later)
6. Click **CREATE**.
7. Modal pops up → click **DOWNLOAD JSON**.

### 3. Move the file into the project

```bash
mv ~/Downloads/client_secret_*.apps.googleusercontent.com.json \
   "/Users/ankitasrivastava/kartik ai agents/accio_legal_demo/secrets/credentials_web.json"
```

(Note the filename — `credentials_web.json`, not `credentials.json`. The
Desktop client's file stays as is.)

### 4. Test locally

```bash
cd "/Users/ankitasrivastava/kartik ai agents/accio_legal_demo"
streamlit run dashboard.py
```

In the browser:

1. Sidebar → click **Settings**
2. You should see "Not connected" status
3. Click **Connect Gmail →**
4. Google sign-in opens → sign in with your own Gmail (testing)
5. Click through the "Google hasn't verified this app" warning
6. Click **Allow**
7. Browser bounces back to `http://localhost:8501/?code=...&state=...`
8. Dashboard auto-routes to Settings page, exchanges the code, shows:
   `✓ Connected. Drafts will now land in: yourname@gmail.com`

That confirms the Web App OAuth flow works end-to-end.

### 5. Hand it to Komal (after Streamlit Cloud deployment)

Once the dashboard is live at `https://accio-legal-demo.streamlit.app/`:

1. Make sure that URL is in the Web client's "Authorized redirect URIs"
   (step 2.5 above)
2. Email Komal:

> Hi Komal — to set up the Gmail integration, click this link, sign in
> with komal@acciolegal.com, click Advanced → Continue past the warning,
> then Allow on the permissions page. Takes 30 seconds.
>
> https://accio-legal-demo.streamlit.app/Settings

3. After she does it, the Settings page shows the token contents in the
   "Advanced" expander
4. You copy the token JSON and paste it into **Streamlit Cloud → app
   settings → Secrets** as:

   ```
   GMAIL_TOKEN_JSON = '''{ "token": "...", "refresh_token": "...", ... }'''
   ```

5. Restart the Streamlit Cloud app. From now on, `gmail_drafts.py`
   reads the token from secrets automatically and creates drafts in
   Komal's Gmail.

## Why this manual paste step

Streamlit Cloud's secrets are read-only at runtime — the dashboard can read
them but not write to them. So once Komal completes OAuth, the resulting
token has to be moved into secrets manually one time. That's a 30-second
copy-paste you do once per user.

If we ever onboard 3+ users we'll switch to a small external database
(Supabase free tier) so token storage becomes automatic. For one user, the
manual paste is fine.
