# Deploying the demo so Komal can use it

The demo runs in mock mode — no API keys, no OAuth, no client data. That
makes it trivial to deploy publicly. Total time: ~10 minutes.

## Recommended: Streamlit Community Cloud (free)

Streamlit Cloud is built specifically for Streamlit apps, free, and deploys
straight from a GitHub repo. Perfect for this.

### What Komal gets

- A URL like `https://accio-legal-demo.streamlit.app`
- Bookmarks it in her browser
- Opens it on her phone or laptop, no install
- Same dashboard you see locally, same interactive flow

### Step-by-step (one-time setup)

**1. Create a GitHub repo and push the code.**

```bash
cd "accio_legal_demo"

# Create a new repo on github.com (private is fine)
# Then add it as a remote and push:

git remote add origin https://github.com/YOUR_USERNAME/accio-legal-demo.git
git branch -M main
git push -u origin main
```

If you already authenticated with `gh` CLI, even faster:

```bash
gh repo create accio-legal-demo --private --source=. --push
```

**2. Sign up for Streamlit Cloud** at [share.streamlit.io](https://share.streamlit.io).
Sign in with the same Google account that owns the GitHub repo. It's free
for unlimited public apps and 1 private app.

**3. Click "New app"** → select the `accio-legal-demo` repo → set:
- Branch: `main`
- Main file path: `dashboard.py`
- App URL: pick a subdomain like `accio-legal-demo`

**4. Click "Deploy"**. Takes ~2 minutes the first time. After that, every
push to `main` auto-redeploys.

**5. Send Komal the URL.** Done.

### Privacy

The default URL is publicly accessible to anyone with the link. For a demo
with fictional client data, this is fine. If you want to gate access:

- Streamlit Cloud has built-in OAuth — go to app settings → "Sharing" →
  add Komal's email + your own as authorized viewers. Anyone else hitting
  the URL gets a Google sign-in prompt.

## Alternatives

| Option | Cost | When to use |
|---|---|---|
| **Streamlit Cloud** | Free | This demo. Best fit. |
| **Render** | Free tier or $7/mo | When you add background workers (Stage 3+ — Drive watcher, Gmail reply watcher). Free tier sleeps after 15 min idle. |
| **Railway** | $5/mo + usage | Same use case as Render. |
| **Hugging Face Spaces** | Free | Public demos. Less polish, but works. |
| **Vercel** | — | Wrong tool for Streamlit. |

You can stay on Streamlit Cloud through the demo phase. When you're ready
to go live with Komal's actual Gmail/Drive (Stage 3+), migrate to Render
because it supports always-on background workers.

## What the deployed demo does NOT do

- Does not call Anthropic API (mock mode only — outputs are pre-baked)
- Does not connect to Komal's Gmail
- Does not watch Komal's Drive for transcripts
- Does not know about Komal's real clients
- Cannot be triggered from anywhere except the dashboard's "Run a Matter" page

For all of those, see the live build path in `GCP_SETUP.md` (Stage 2 onward).

## Updating the deployed demo

Any future change to the code:

```bash
git add .
git commit -m "Tweak proposal styling" -m "(or whatever)"
git push
```

Streamlit Cloud auto-redeploys within ~30 seconds.

## Checklist before sending Komal the URL

- [ ] Open the URL in incognito to confirm it loads
- [ ] Click "Run a Matter" → run all three scenarios (Velara, Niramai, Glyph)
- [ ] Verify both download buttons (HTML, Word) produce real files
- [ ] Verify the inline HTML preview renders the cover + phase blocks correctly
- [ ] Open one of the downloaded `.docx` engagement letters in Word and check
  the client party block, scope table, and signature block all look right
- [ ] If you've enabled access gating, add Komal's email to the viewer list
