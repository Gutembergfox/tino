# Tino

Tino is a register-calibration assistant for Brazilian learners of English. It uses a variationist-sociolinguistic lens to identify conversational intrusions, explain likely Brazilian Portuguese (L1) transfer, and suggest context-appropriate alternatives.

Tino is not a grammar checker. Its goal is to help learners move between academic, professional, and casual registers without treating Brazilian Portuguese as a defect.

**Project status:** AI-assisted prototype. Register and transfer explanations are hypotheses requiring review; model accuracy and educational efficacy have not been established. See the [offline tests](docs/TESTING.md) and [provisional evaluation protocol](evaluation/README.md).

## Live demo

https://tino-deploy.vercel.app

## Features

- Analyze English texts from 50 to 500 words.
- Choose an academic, professional, or casual target context.
- Receive a structured JSON analysis in Brazilian Portuguese or English.
- Identify likely transfer patterns such as `like`/`tipo`, `actually`/`atualmente`, `parents`/`parentes`, and conversational tag questions.
- Switch the interface between Portuguese and English.
- Translate an existing report into English while preserving learner quotes and suggestions.
- Copy an ABNT software citation from each generated report, including its access timestamp.
- Install the site as a PWA on supported Android and desktop browsers.
- Analyze Brazilian Portuguese register with the dedicated `/analyze-pt` route, including optional lenses from Jespersen's Cycle and Van Gelderen's linguistic cycles.
- Read the project's sociolinguistic rationale at `/about`.

## Local setup

1. Create and activate a virtual environment (recommended):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root:

   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

4. Start the development server:

   ```bash
   uvicorn main:app --reload
   ```

5. Open http://127.0.0.1:8000.

## How it works

The FastAPI backend serves `index.html`, validates the submitted text and context, sends the request to the OpenAI Responses API using `gpt-5.6`, and parses the model output as JSON. The full sociolinguistic instruction set lives in the `SYSTEM_PROMPT` constant in `main.py`.

The frontend renders the overall assessment, register-break annotations, transfer hypotheses, rewrite suggestions, and recurring transfer patterns. The OpenAI API key remains server-side and is never sent to the browser.

The frontend can request `/translate` when the user switches a completed report to English. Reports also include a copyable ABNT reference for the software. `manifest.webmanifest` and `service-worker.js` provide installable PWA behavior; the service worker uses versioned cache names so UI updates invalidate older cached assets.

## How Codex and GPT-5.6 were used

This project was built with Codex as the primary development collaborator. Codex was used to shape the product concept, scaffold the FastAPI MVP, implement the bilingual frontend, integrate and debug the OpenAI Responses API, generate the mascot asset, write the sociolinguistic project pitch and technical documentation, run model smoke tests, and deploy the application to Vercel.

GPT-5.6 is the runtime model behind Tino's analysis. It receives the project's sociolinguistic system prompt together with the learner's English text and declared target context, then returns structured JSON containing the overall assessment, register-break annotations, transfer hypotheses, and rewrite suggestions. The current offline suite validates software behaviour with mocked Responses API outputs. It does not measure the runtime model's linguistic quality. The former smoke script called Chat Completions and attempted JSON parsing without assertions.

Codex accelerated the workflow by turning sociolinguistic requirements into a working product loop: prompt design, API contract, UI rendering, test fixture, deployment configuration, and judge-facing documentation were developed and checked together.

## Deploying to Vercel

The repository includes `api/index.py` and `vercel.json` for Vercel deployment:

1. Import the repository at https://vercel.com/new.
2. Add `OPENAI_API_KEY` under **Settings → Environment Variables** for the Production environment.
3. Deploy or redeploy the project.

Do not commit `.env`. It is excluded by `.gitignore`.

## Project structure

```text
main.py              FastAPI app and system prompt
index.html           Main interface
about.html           Sociolinguistic project pitch
assets/              Mascot and brand assets
api/index.py         Vercel serverless entry point
vercel.json          Vercel routing configuration
requirements.txt     Python dependencies
```

## Research basis

The project treats register as language associated with a situation of use and the functions performed by its linguistic features. It draws on audience design and on research about cross-linguistic influence in second-language learning. See the references on the [About page](https://tino-deploy.vercel.app/about).

## License and attribution

Tino by Rapôso, 2026.

## Testing without paid API calls

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
python evaluation/validate_cases.py
```

See [testing instructions](docs/TESTING.md), the [output schema](schemas/analysis.schema.json), and the [linguistic evaluation protocol](evaluation/README.md). The offline suite mocks the provider and blocks network sockets. A passing suite is evidence about the software contract, not model accuracy.

The new tests, schema, evaluation cases and documentation were developed with AI assistance and executed in an isolated environment. The synthetic linguistic cases still require independent review.

These changes are prepared on a review branch because the repository's development guide states that pushes to main can trigger production deployment. Merging should follow a separate deployment decision.
