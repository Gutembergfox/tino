# Development Guide

## Requirements

- Python 3.10 or newer
- An OpenAI API key with access to `gpt-5.6`
- Git

## Local workflow

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000` and use a 50–500 word English sample.

## Environment variables

Create `.env` locally:

```env
OPENAI_API_KEY=your_api_key_here
```

Never commit `.env`. The repository `.gitignore` excludes it. On Vercel, set the same variable in the project's Environment Variables settings.

## Validation checklist

Before pushing changes:

```bash
python3 -m py_compile main.py
```

Then verify manually:

1. `/` loads the interface and mascot.
2. `/about` loads the pitch and references.
3. PT/EN switching updates the interface.
4. Text shorter than 50 words is rejected client-side.
5. A valid sample returns annotations or an explicit no-issues assessment.

## Prompt changes

Keep the system prompt's output contract synchronized with the frontend. If you rename a JSON field, update `main.py`, the rendering code in `index.html`, and the example in `docs/API.md` together.

## Deployment

From the project root, deploy with:

```bash
vercel --prod
```

For GitHub-connected deployments, push to `main` and let the linked Vercel project build the new revision. Confirm that `OPENAI_API_KEY` is configured for the target environment.
