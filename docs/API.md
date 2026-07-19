# Tino API

Base URL (production): `https://tino-deploy.vercel.app`

## `GET /`

Returns the main Tino interface.

## `GET /about`

Returns the project pitch and sociolinguistic rationale.

## `GET /assets/{filename}`

Serves project assets such as `tino-mascot.png`.

## `POST /analyze`

Analyzes an English text against a target register.

### Request

```json
{
  "text": "An English text between fifty and five hundred words.",
  "context": "academic"
}
```

`context` must be one of `academic`, `professional`, or `casual`. The backend also enforces the 50–500 word limit.

### Successful response

```json
{
  "target_register": "academic",
  "overall_assessment": "A Brazilian Portuguese assessment of the dominant register pattern.",
  "annotations": [
    {
      "quote": "you know",
      "issue": "Marcador conversacional",
      "register_break": "Intrusão de registro conversacional",
      "transfer_hypothesis": "Possível transferência de né?",
      "why_it_fails": "A marca de oralidade desloca o texto do registro acadêmico.",
      "rewrite_suggestion": "The evidence suggests that..."
    }
  ],
  "transfer_pattern_summary": "Resumo de dois ou três padrões recorrentes."
}
```

### Error responses

- `422`: invalid context or text length.
- `500`: missing `OPENAI_API_KEY`.
- `502`: OpenAI request failure or invalid model JSON.

The frontend intentionally displays a localized generic error instead of exposing provider or credential details.

## `POST /translate`

Translates a completed Portuguese report for the English interface. The endpoint preserves the JSON structure and annotation count, translates explanatory fields, and leaves learner quotes and English rewrite suggestions unchanged.

### Request

```json
{
  "analysis": {
    "target_register": "academic",
    "overall_assessment": "...",
    "annotations": [],
    "transfer_pattern_summary": "..."
  }
}
```

## `POST /analyze-pt`

Analyzes Brazilian Portuguese text for academic, professional, or casual register. It returns the same JSON shape as `/analyze`, with natural-language fields in Brazilian Portuguese. The prompt may use Jespersen's Cycle and Van Gelderen's linguistic-cycle framework when the text provides evidence; it does not treat language change or variation as an error.

## Installable web app and citations

`GET /manifest.webmanifest` and `GET /service-worker.js` support PWA installation. Generated reports show a copyable ABNT reference identifying Tino as software and recording the analysis access date and time. The fixed software reference is also listed on `/about`.
