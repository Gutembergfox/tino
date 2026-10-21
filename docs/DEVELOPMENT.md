# Development Guide

## Requirements

- Python 3.10 or newer
- No API key for offline tests; a separately authorized API key is needed only for live analysis
- Git

## Local workflow

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000` and use a 50–500 word English sample.

## Environment variables

Create `.env` locally:

```env
OPENAI_API_KEY=your_api_key_here
```

Never commit `.env`. The repository `.gitignore` excludes it. On Vercel, set the same variable in the project's Environment Variables settings.

## Offline verification first

Run `python -m pytest` and `python evaluation/validate_cases.py` before considering any live request. See [TESTING.md](TESTING.md). Do not use real keys or model calls in CI.

## Validation checklist

Before pushing changes:

```bash
python3 -m py_compile main.py
```

The following manual checks are separate from the offline suite. Analysis requests require explicit authorization for provider costs:


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
