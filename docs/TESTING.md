# Sociolinguistic Model Testing

## Purpose

`test_tino.py` is a direct smoke test for Tino's model instruction set. It bypasses the browser and FastAPI route so that model behavior and JSON serialization can be checked independently.

## Run the test

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 test_tino.py
```

The project must have a local `.env` containing `OPENAI_API_KEY`. The key is read by `python-dotenv` and is never printed.

## Test fixture

The fixture is an English paragraph submitted for the academic register. It intentionally includes:

- discourse openers such as `So`;
- conversational engagement markers such as `You know`;
- filler `Like`;
- the false cognates `pretend` and `actually`;
- the Portuguese calque `Thanks God`;
- a dative-subject pattern beginning with `For me`.

These forms are chosen because they let the test distinguish register calibration from generic grammar correction.

## Expected output

The model should return valid JSON with these top-level fields:

- `target_register`;
- `overall_assessment`;
- `annotations`;
- `transfer_pattern_summary`.

Natural-language fields should be in Brazilian Portuguese. `quote` and `rewrite_suggestion` should remain in English. Each annotation should explain the likely Portuguese transfer mechanism and why the form is or is not appropriate for the academic context.

## Troubleshooting

- **Missing key:** confirm that `.env` is in the project root and contains `OPENAI_API_KEY`.
- **Connection error:** check network access and the OpenAI account's API access.
- **Invalid JSON:** inspect the raw response printed by the script and verify that the system prompt still requires strict JSON.
- **Model access error:** verify that the configured account can use `gpt-5.6`.
