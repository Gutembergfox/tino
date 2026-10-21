# Offline software tests and linguistic evaluation

## Run without a key or provider access

Tested with Python 3.13 in an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest
python evaluation/validate_cases.py
```

Dependency installation needs access to the package registry. The tests themselves block network sockets with pytest-socket; only local Unix sockets used by Python's event loop are allowed. Test imports suppress dotenv loading and remove any existing OPENAI_API_KEY. Provider calls are mocked with an inert placeholder. There are no model calls, live credentials or paid API tests.

`python test_tino.py` is a compatibility entry point for this same offline suite. It replaces the historical script that called Chat Completions and merely attempted JSON parsing.

## What is checked

- English 50/500-word boundaries; Portuguese limits and invalid registers.
- Responses API call construction for both analysis routes.
- Schema-valid no-change output with an empty annotation list.
- Invalid JSON, missing/wrong fields, hallucinated quotes and mismatched registers.
- Missing credentials and sanitized provider errors.
- Translation preservation of register, annotation count, quotes and rewrite suggestions.
- Structure and endpoint compatibility of the provisional evaluation cases.

The JSON contract is in [analysis.schema.json](../schemas/analysis.schema.json). The backend validates its typed equivalent before returning a model report. Schema tests do not establish natural-language correctness.

## What is not checked

No live model quality, latency, provider availability, deployment behaviour, browser rendering or educational impact is established by this suite. The [linguistic evaluation protocol](../evaluation/README.md) describes a separate, not-yet-run process including no-change cases and human review. Historical README statements that the old smoke script checked expected fields or linguistic behaviour were too strong: it contained no assertions.

## Verified execution

On 21 October 2026, **33 tests passed** in a clean Linux Python 3.13.13 virtual environment installed from `requirements-dev.txt` and the pinned constraints. `pip check` reported no broken requirements. An additional offline SDK transport test exercises the installed OpenAI client's real Responses serialization and output parsing through an in-memory HTTPX2 transport; it makes no network request. The provisional case validator accepted 12 cases, including six explicit no-change cases.

The original connected-computer execution service became unavailable. Verification used an isolated remote sandbox with public source files only. Production deployment and live model evaluation were not performed.
