# Tino Architecture

## Overview

Tino is a small, stateless web application with a FastAPI backend and a single-page HTML frontend. There is no database, authentication layer, session store, or application-owned user data.

```text
Browser
  │
  ├── GET /             ──> FastAPI serves index.html
  ├── GET /about        ──> FastAPI serves about.html
  ├── GET /assets/*     ──> FastAPI StaticFiles serves the mascot
  └── POST /analyze     ──> OpenAI Responses API (gpt-5.6)
```

## Backend

`main.py` creates the FastAPI application, loads environment variables with `python-dotenv`, validates requests with Pydantic, and calls the OpenAI Python SDK.

The `SYSTEM_PROMPT` constant defines Tino's role, register model, Brazilian Portuguese transfer patterns, output schema, and language policy. The endpoint adds the selected context and learner text to that instruction set.

The backend rejects unsupported contexts and texts outside the 50–500 word range. It parses the model's JSON response before returning it to the browser.

## Frontend

`index.html` is a dependency-light frontend using Tailwind CSS from its CDN. It provides:

- client-side word counting and validation;
- academic, professional, and casual context selection;
- PT/EN interface switching;
- safe DOM rendering with `textContent`;
- loading, error, empty-result, and annotation states.

`about.html` is a static project pitch with the sociolinguistic rationale and ABNT references.

## Deployment

Vercel detects the Python dependencies and deploys the FastAPI app as a serverless function. `api/index.py` exports the `app` object, while `vercel.json` routes requests to that entry point. `OPENAI_API_KEY` must be configured as a Vercel environment variable and is never committed.

## Design principles

1. **Register before correction:** analyze situational appropriateness before discussing form.
2. **Transfer as evidence, not deficiency:** explain L1 influence as a meaningful learner strategy.
3. **Structured output:** keep model responses predictable for the frontend.
4. **Stateless privacy:** do not persist submitted text or analysis results.
5. **Progressive disclosure:** show a concise overall reading first, then detailed annotations.
