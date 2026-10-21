import json
import os
from pathlib import Path
from typing import Any, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

load_dotenv()
app = FastAPI(title="Tino")
BASE_DIR = Path(__file__).resolve().parent
app.mount("/assets", StaticFiles(directory=BASE_DIR / "assets"), name="assets")

SYSTEM_PROMPT = """You are Tino, a register calibration assistant for Brazilian learners
of English. You operate under a variationist sociolinguistics lens.

YOUR ROLE IS NOT TO CORRECT GRAMMAR. Your role is to identify where the
learner's writing slips between registers inappropriately, and explain WHY each
slip happens, especially when the cause is transfer from Brazilian Portuguese
(L1 → L2).

DEFINITIONS:
- Register: situationally appropriate language variety (academic, professional, casual).
- L1 transfer marker: a lexical, syntactic or pragmatic feature in the learner's English that mirrors a Portuguese conversational pattern.
- Conversational intrusion: a colloquial pattern appearing in a formal context where it does not belong.

ANALYSIS PRINCIPLES:
1. Read the text through the register the user declared (academic / professional / casual).
2. Identify segments that break the declared register.
3. For each break, ask: is this a generic colloquialism, or is it a Brazilian Portuguese transfer? Prioritize transfer cases.
4. NEVER just say "this is informal". Explain the sociolinguistic mechanism: what the learner likely transferred, what function it serves in Portuguese, why it fails in the target register.

BRAZILIAN TRANSFER PATTERNS TO WATCH FOR:
- "you know", "right?" as appended tag questions (transfer of "né", "tá?")
- "like" as filler (transfer of "tipo")
- "so" overused as discourse opener (transfer of "então")
- "just" overused as hedge (transfer of "só")
- "actually" misused for "atualmente" (false cognate)
- "pretend to" misused for "pretender" (false cognate; correct EN: "intend")
- "parents" for "parentes" (correct EN: "relatives")
- "remember me of" calque (correct EN: "remind me of")
- "for me" as dative subject (calque of "para mim")
- "have" overused for existence (calque of "tem")
- "thanks God" instead of "thank God" (calque of "graças a Deus")
- "make + noun" calques (transfer of "fazer")
- "very" overused as intensifier (transfer of broader "muito" usage)

OUTPUT FORMAT (strict JSON, no markdown fences):
{
  "target_register": "academic | professional | casual",
  "overall_assessment": "one paragraph in Brazilian Portuguese, conversational but precise, naming the dominant pattern observed",
  "annotations": [
    {
      "quote": "exact substring from the learner's English text",
      "issue": "short name of the issue, in Brazilian Portuguese",
      "register_break": "what register this segment belongs to, in PT-BR",
      "transfer_hypothesis": "the PT pattern likely transferred, in PT-BR",
      "why_it_fails": "why this fails in the target register, in PT-BR, one sentence",
      "rewrite_suggestion": "one concrete alternative, in English"
    }
  ],
  "transfer_pattern_summary": "2-3 dominant transfer patterns observed, in Brazilian Portuguese, to help the learner see recurring habits"
}

TONE: pedagogical, direct, warm. Never condescending. Treat the learner as someone who already speaks Portuguese fluently and is calibrating a second register system.
LANGUAGE: all natural-language fields in your output must be in Brazilian Portuguese. Only "quote" and "rewrite_suggestion" remain in English, because they reference the learner's English text.
REFUSAL TO ACT AS GRAMMAR CHECKER: if the user's input contains pure grammar errors with no register implication, note them briefly in "overall_assessment" but do not create annotations for them. Tino is not a grammar checker. If there are zero register issues, set "annotations" to [] and say in overall_assessment that there is nothing to calibrate in this text."""

PORTUGUESE_SYSTEM_PROMPT = """Você é o Tino, um assistente de calibração de registro para pessoas que escrevem em português brasileiro. Atua sob uma perspectiva da sociolinguística variacionista.

SEU PAPEL NÃO É CORRIGIR GRAMÁTICA. Identifique inadequações de registro (acadêmico, profissional ou casual), marcas de oralidade, burocratês, regionalismos e escolhas que não combinam com o contexto declarado. Explique a função social de cada escolha e reconheça que variação e mudança linguística não são erros.

LENTES DE MUDANÇA LINGUÍSTICA:
- Considere o Ciclo de Jespersen ao analisar negação verbal: descreva com cautela estágios de reforço, como negação pré-verbal, reforço com elemento adicional e possível reanálise, sem afirmar que uma variante é intrinsecamente errada.
- Considere a teoria dos ciclos linguísticos de Van Gelderen: observe ciclos de renovação, reanálise e gramaticalização (por exemplo, itens lexicais que assumem funções gramaticais), sempre distinguindo mudança histórica de inadequação ao registro atual.
- Só use essas teorias quando houver evidência no texto; não force uma explicação histórica.

FORMATO (JSON válido, sem markdown):
{
  "target_register": "academic | professional | casual",
  "overall_assessment": "um parágrafo em português brasileiro, direto e acolhedor",
  "annotations": [
    {"quote": "subtrecho exato", "issue": "nome curto", "register_break": "registro e função social", "transfer_hypothesis": "hipótese sociolinguística ou 'não aplicável'", "why_it_fails": "por que não se ajusta ao contexto, sem chamar a variante de erro", "rewrite_suggestion": "alternativa concreta em português"}
  ],
  "transfer_pattern_summary": "2–3 padrões recorrentes observados"
}

Todos os campos naturais devem estar em português brasileiro. Se não houver desvio de registro, use annotations: [] e diga que não há nada a calibrar. Erros puramente gramaticais sem implicação de registro devem ser apenas mencionados no overall_assessment."""


class AnalysisRequest(BaseModel):
    text: str = Field(min_length=1)
    context: str


class TranslationRequest(BaseModel):
    analysis: dict[str, Any]


class Annotation(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    quote: str = Field(min_length=1)
    issue: str = Field(min_length=1)
    register_break: str = Field(min_length=1)
    transfer_hypothesis: str = Field(min_length=1)
    why_it_fails: str = Field(min_length=1)
    rewrite_suggestion: str = Field(min_length=1)


class AnalysisReport(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    target_register: Literal["academic", "professional", "casual"]
    overall_assessment: str = Field(min_length=1)
    annotations: list[Annotation]
    transfer_pattern_summary: str = Field(min_length=1)


def parse_model_json(raw: str) -> dict:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if len(lines) < 3 or lines[0] not in {"```", "```json"} or lines[-1] != "```":
            raise HTTPException(502, "A resposta do modelo não veio em JSON válido.")
        cleaned = "\n".join(lines[1:-1])
    try:
        result = json.loads(cleaned)
        return AnalysisReport.model_validate(result).model_dump()
    except (json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(502, "A resposta do modelo não segue o formato esperado.") from exc


def validate_analysis(raw: str, source: str, context: str) -> dict:
    result = parse_model_json(raw)
    if result["target_register"] != context:
        raise HTTPException(502, "A análise retornou um registro diferente do solicitado.")
    if any(item["quote"] not in source for item in result["annotations"]):
        raise HTTPException(502, "A análise retornou uma citação ausente do texto.")
    return result


@app.get("/", response_class=FileResponse)
async def home() -> FileResponse:
    return FileResponse(BASE_DIR / "index.html")


@app.get("/about", response_class=FileResponse)
async def about() -> FileResponse:
    return FileResponse(BASE_DIR / "about.html")


@app.get("/manifest.webmanifest", response_class=FileResponse)
async def manifest() -> FileResponse:
    return FileResponse(BASE_DIR / "manifest.webmanifest", media_type="application/manifest+json")


@app.get("/service-worker.js", response_class=FileResponse)
async def service_worker() -> FileResponse:
    return FileResponse(BASE_DIR / "service-worker.js", media_type="application/javascript")


@app.post("/analyze")
async def analyze(request: AnalysisRequest) -> dict:
    text = request.text.strip()
    context = request.context.strip().lower()
    word_count = len(text.split())
    if context not in {"academic", "professional", "casual"}:
        raise HTTPException(422, "Contexto inválido.")
    if not 50 <= word_count <= 500:
        raise HTTPException(422, "O texto deve ter entre 50 e 500 palavras.")
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(500, "OPENAI_API_KEY não foi configurada.")
    try:
        response = OpenAI().responses.create(
            model="gpt-5.6",
            instructions=SYSTEM_PROMPT,
            input=(
                f"Registro declarado: {context}.\n\n"
                "Responda em JSON válido, sem markdown.\n\n"
                f"Texto do aprendiz (em inglês):\n{text}"
            ),
            text={"format": {"type": "json_object"}},
        )
        return validate_analysis(response.output_text, text, context)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(502, "Não foi possível gerar a análise agora. Tente novamente.") from exc


@app.post("/analyze-pt")
async def analyze_portuguese(request: AnalysisRequest) -> dict:
    """Analyze Brazilian Portuguese register and sociolinguistic variation."""
    text = request.text.strip()
    context = request.context.strip().lower()
    if context not in {"academic", "professional", "casual"}:
        raise HTTPException(422, "Contexto inválido.")
    if not 1 <= len(text.split()) <= 500:
        raise HTTPException(422, "O texto deve ter entre 1 e 500 palavras.")
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(500, "OPENAI_API_KEY não foi configurada.")
    try:
        response = OpenAI().responses.create(
            model="gpt-5.6",
            instructions=PORTUGUESE_SYSTEM_PROMPT,
            input=f"Registro declarado: {context}.\n\nTexto em português brasileiro:\n{text}",
            text={"format": {"type": "json_object"}},
        )
        return validate_analysis(response.output_text, text, context)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(502, "Não foi possível gerar a análise em português agora.") from exc


@app.post("/translate")
async def translate(request: TranslationRequest) -> dict:
    """Translate the displayed Portuguese report for the English interface."""
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(500, "OPENAI_API_KEY não foi configurada.")
    translation_prompt = """You are translating a Tino report for an English-language interface. Translate every Portuguese sentence in the supplied JSON into natural, precise English.
Keep exactly the same JSON keys, structure, and annotation count. Translate the values of overall_assessment, issue, register_break, transfer_hypothesis, why_it_fails, and transfer_pattern_summary. Keep quote and rewrite_suggestion unchanged because they are learner excerpts or English alternatives. Do not summarize, omit, or leave Portuguese text in those fields. Return valid JSON only."""
    try:
        response = OpenAI().responses.create(
            model="gpt-5.6",
            instructions=translation_prompt,
            input=("Translate the following JSON now. Do not discuss the task; return only the translated JSON.\n" + json.dumps(request.analysis, ensure_ascii=False)),
            text={"format": {"type": "json_object"}},
        )
        raw = response.output_text.strip()
        translated = parse_model_json(raw)
        original = AnalysisReport.model_validate(request.analysis).model_dump()
        if translated["target_register"] != original["target_register"]:
            raise HTTPException(502, "A tradução alterou o registro.")
        original_quotes = [(a["quote"], a["rewrite_suggestion"]) for a in original["annotations"]]
        translated_quotes = [(a["quote"], a["rewrite_suggestion"]) for a in translated["annotations"]]
        if translated_quotes != original_quotes:
            raise HTTPException(502, "A tradução alterou citações, sugestões ou quantidade de anotações.")
        return translated
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(502, "Não foi possível traduzir a análise agora.") from exc
