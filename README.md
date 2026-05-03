# Accio Legal — Proposal & Engagement Letter Pipeline (v1 demo)

Turns a first-call transcript into a Komal-voice proposal draft, then turns the client's acceptance email into a filled engagement letter — both as `.docx` files.

## What this demo shows Komal

1. Otter-style transcript goes in.
2. Claude extracts client, scope, and pricing into a structured form.
3. **Checkpoint** — terminal shows what was heard from the call. Komal confirms or types corrections in plain English ("Phase II fee is 38000, not 35000").
4. Claude drafts the full proposal in Accio's voice using Kalolytic as a style reference.
5. Proposal `.docx` is saved to `output/`.
6. Demo pauses. Pretend Komal sent it and the client replied.
7. Sample acceptance email is read. Claude classifies (accept / negotiate / reject) and extracts confirmed signatory info.
8. Komal's existing engagement letter `.docx` template is filled in:
   - Effective date
   - Client party block (inserted under "BY AND BETWEEN")
   - Annexure A scope table (Service / TAT / Pricing INR)
   - Client email and signatory name
   - Consultant address
9. Engagement letter `.docx` is saved to `output/`.

In production, the transcript comes from Otter's webhook and the reply from a Gmail watcher; both drafts land as Gmail drafts in Komal's inbox.

## Setup

```bash
cd "accio_legal_demo"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and put your real ANTHROPIC_API_KEY
export $(cat .env | xargs)
```

## Run

```bash
python run_demo.py
```

Outputs land in `output/`:
- `Velara_Proposal.docx`
- `Velara_Engagement_Letter.docx`

## Files

```
accio_legal_demo/
├── run_demo.py                              main script
├── style/kalolytic_proposal.txt             style reference for Claude
├── templates/engagement_template.docx       Komal's EL template (verbatim)
├── samples/transcript.txt                   mock first-call (replace with Otter export)
├── samples/client_reply.txt                 mock acceptance email (replace with Gmail body)
├── output/                                  generated drafts land here
├── requirements.txt
└── .env.example
```

## What's NOT in v1 (deferred)

- Otter webhook → transcript ingestion (manual file for now)
- Gmail API → draft creation, reply watching (manual files for now)
- WhatsApp/Slack ping for the checkpoint (terminal prompt for now)
- SharePoint matter folders, Toggl projects, full intake form, onboarding pack

These are the natural next layer once Komal validates the core flow.

## Editing for new matter types

To add support for a new matter type (e.g. trademark filing, contract drafting):

1. Drop a representative past proposal as text into `style/`.
2. Update `STYLE_REF_PATH` (or load multiple) in `run_demo.py` so Claude has voice samples for that matter type.
3. The phase library is implicit in the style references — no code change needed.

## Cost per matter (rough)

Three Claude API calls per matter (extract, draft proposal, classify reply), plus optionally a corrections call. With prompt caching on the system block, expect well under USD $0.20 per matter end-to-end on `claude-sonnet-4-6`.
