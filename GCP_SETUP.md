# Google Cloud setup — one-time, ~5 minutes

This connects the pipeline to Komal's Gmail and Google Drive. Do this once
under your own Google Cloud account; Komal grants consent as a test user.

## 1. Create a project

[console.cloud.google.com](https://console.cloud.google.com) → top dropdown
→ "New Project" → name it `Accio Legal Pilot` → Create.

## 2. Enable the APIs

In the project, go to **APIs & Services → Library** and enable:
- Gmail API
- Google Drive API
- Google Calendar API (needed in Stage 3 for filtering intake calls)

## 3. Configure the OAuth consent screen

**APIs & Services → OAuth consent screen** → User type: **External** → Create.

Fill in:
- App name: `Accio Legal Pilot`
- User support email: your email
- Developer contact: your email
- Save and continue.

Scopes (click "Add or Remove Scopes"):
- `gmail.compose`
- `gmail.readonly`
- `drive.readonly`
- `calendar.readonly`

Test users → Add: `komal@acciolegal.com` (and your own email so you can test
first).

## 4. Create the OAuth client

**APIs & Services → Credentials → Create Credentials → OAuth client ID**.

- Application type: **Desktop app**
- Name: `Accio Legal Pilot Desktop`
- Click Create, then **Download JSON**.

Save that file as `secrets/credentials.json` next to `run_demo.py`.

## 5. Run the auth flow

```bash
cd "accio_legal_demo"
python3 setup_gmail_oauth.py
```

A browser opens. Sign in with the Google account you want drafts in (start
with your own to test, then re-run once Komal is added). Click through the
"Google hasn't verified this app" warning (that's expected for a test app)
and grant the requested permissions.

A `secrets/token.json` is written. You're done.

## 6. Test it

```bash
python3 run_demo.py --mock --gmail-draft
```

Both prompts auto-confirm with `printf '\n\n' |` if you want to skip the
checkpoint pause:

```bash
printf '\n\n' | python3 run_demo.py --mock --gmail-draft
```

A proposal draft and an engagement letter draft should appear in the
authenticated account's Gmail Drafts folder, addressed to
`rohan@velarabio.com`. Open Gmail → Drafts to see them.

## When to swap from your account to Komal's

Once the flow is verified end-to-end with your own Gmail:

1. Delete `secrets/token.json`
2. Have Komal sit with you (or share screen) and re-run `python3 setup_gmail_oauth.py`
3. She signs in with `komal@acciolegal.com` and grants consent
4. New `token.json` is hers — drafts now land in her Gmail

The `credentials.json` (the OAuth client) doesn't change — that stays the
same regardless of which user is authenticated.

## Notes on the "unverified app" warning

Until you submit the app for verification by Google, anyone using it sees a
"Google hasn't verified this app" warning. For a test/internal pilot with
fewer than 100 users, this is fine — you stay under Google's "Testing"
status indefinitely. Verification is only required when you want to remove
the warning OR exceed 100 users.

## Token storage in production (Render)

When deploying to Render, copy the contents of `secrets/token.json` into a
Render environment variable (e.g. `GMAIL_TOKEN_JSON`) and load it at runtime
instead of reading from disk. Same for `credentials.json` →
`GMAIL_CREDENTIALS_JSON`. Don't commit either file to git.
