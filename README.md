# Tino

Tino is a register-calibration assistant for Brazilian learners of English. It uses a variationist-sociolinguistic lens to identify conversational intrusions, explain likely Brazilian Portuguese (L1) transfer, and suggest context-appropriate alternatives.

Tino is not a grammar checker. Its goal is to help learners move between academic, professional, and casual registers without treating Brazilian Portuguese as a defect.

## Live demo

https://tino-deploy.vercel.app

## Features

- Analyze English texts from 50 to 500 words.
- Choose an academic, professional, or casual target context.
- Receive a structured JSON analysis in Brazilian Portuguese or English.
- Identify likely transfer patterns such as `like`/`tipo`, `actually`/`atualmente`, `parents`/`parentes`, and conversational tag questions.
- Switch the interface between Portuguese and English.
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
