import asyncio
import copy
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from fastapi import HTTPException
from jsonschema import Draft202012Validator

REPORT = {
    "target_register": "academic",
    "overall_assessment": "Não há inadequações de registro nesta amostra.",
    "annotations": [],
    "transfer_pattern_summary": "Nenhum padrão de transferência identificado.",
}
TEXT = " ".join(["sample"] * 50)
SCHEMA = json.loads((Path(__file__).parents[1] / "schemas/analysis.schema.json").read_text())


def api(app, path, payload):
    async def call():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.post(path, json=payload)
    return asyncio.run(call())


def provider(module, monkeypatch, report=None):
    monkeypatch.setenv("OPENAI_API_KEY", "offline-placeholder-not-a-credential")
    mock = Mock()
    mock.responses.create.return_value = SimpleNamespace(
        output_text=json.dumps(REPORT if report is None else report)
    )
    constructor = Mock(return_value=mock)
    monkeypatch.setattr(module, "OpenAI", constructor)
    return constructor, mock


def test_schema_accepts_no_change():
    Draft202012Validator.check_schema(SCHEMA)
    Draft202012Validator(SCHEMA).validate(REPORT)


@pytest.mark.parametrize("raw", [
    "not json", "[]", "null", "{}", "```", "```json\n{}", '{"annotations": "wrong"}',
])
def test_invalid_model_output_is_502(app_module, raw):
    with pytest.raises(HTTPException) as error:
        app_module.parse_model_json(raw)
    assert error.value.status_code == 502


def test_fenced_json(app_module):
    assert app_module.parse_model_json("```json\n" + json.dumps(REPORT) + "\n```") == REPORT


@pytest.mark.parametrize("field,value", [
    ("target_register", "formal"), ("overall_assessment", 123),
    ("annotations", {}), ("transfer_pattern_summary", ""),
])
def test_contract_rejects_wrong_fields(app_module, field, value):
    report = {**REPORT, field: value}
    assert list(Draft202012Validator(SCHEMA).iter_errors(report))
    with pytest.raises(HTTPException):
        app_module.parse_model_json(json.dumps(report))


@pytest.mark.parametrize("route,text", [("/analyze", TEXT), ("/analyze-pt", "Olá.")])
def test_routes_use_responses_api_and_allow_no_change(app_module, monkeypatch, route, text):
    _, mock = provider(app_module, monkeypatch)
    response = api(app_module.app, route, {"text": text, "context": " ACADEMIC "})
    assert response.status_code == 200
    assert response.json() == REPORT
    Draft202012Validator(SCHEMA).validate(response.json())
    kwargs = mock.responses.create.call_args.kwargs
    assert kwargs["text"] == {"format": {"type": "json_object"}}
    assert text in kwargs["input"]
    assert kwargs["instructions"] == (
        app_module.SYSTEM_PROMPT if route == "/analyze" else app_module.PORTUGUESE_SYSTEM_PROMPT
    )
    mock.chat.completions.create.assert_not_called()


@pytest.mark.parametrize("route,n,context", [
    ("/analyze", 49, "academic"), ("/analyze", 501, "academic"),
    ("/analyze-pt", 0, "casual"), ("/analyze-pt", 501, "professional"),
    ("/analyze", 50, "invalid"),
])
def test_invalid_input_does_not_call_provider(app_module, monkeypatch, route, n, context):
    constructor, _ = provider(app_module, monkeypatch)
    response = api(app_module.app, route, {"text": " ".join(["word"] * n), "context": context})
    assert response.status_code == 422
    constructor.assert_not_called()


@pytest.mark.parametrize("n", [50, 500])
def test_english_boundaries(app_module, monkeypatch, n):
    provider(app_module, monkeypatch)
    assert api(app_module.app, "/analyze", {"text": " ".join(["word"] * n), "context": "academic"}).status_code == 200


def test_missing_key(app_module, monkeypatch):
    constructor = Mock()
    monkeypatch.setattr(app_module, "OpenAI", constructor)
    assert api(app_module.app, "/analyze", {"text": TEXT, "context": "academic"}).status_code == 500
    constructor.assert_not_called()


def test_provider_failure_is_sanitized(app_module, monkeypatch):
    _, mock = provider(app_module, monkeypatch)
    mock.responses.create.side_effect = RuntimeError("private provider detail")
    response = api(app_module.app, "/analyze", {"text": TEXT, "context": "academic"})
    assert response.status_code == 502
    assert "private provider detail" not in response.text


def annotation(quote="sample"):
    return {key: value for key, value in zip(
        ["quote", "issue", "register_break", "transfer_hypothesis", "why_it_fails", "rewrite_suggestion"],
        [quote, "Exemplo", "Formal", "Hipótese, não diagnóstico", "Contexto", "example"],
    )}


def test_hallucinated_quote_rejected(app_module, monkeypatch):
    provider(app_module, monkeypatch, {**REPORT, "annotations": [annotation("absent quote")]})
    assert api(app_module.app, "/analyze", {"text": TEXT, "context": "academic"}).status_code == 502


def test_wrong_register_rejected(app_module, monkeypatch):
    provider(app_module, monkeypatch, {**REPORT, "target_register": "casual"})
    assert api(app_module.app, "/analyze", {"text": TEXT, "context": "academic"}).status_code == 502


def test_translate_preserves_quotes_and_suggestions(app_module, monkeypatch):
    original = {**REPORT, "annotations": [annotation()]}
    translated = {**copy.deepcopy(original), "overall_assessment": "Example assessment."}
    provider(app_module, monkeypatch, translated)
    response = api(app_module.app, "/translate", {"analysis": original})
    assert response.status_code == 200
    assert response.json()["annotations"] == original["annotations"]


@pytest.mark.parametrize("change", ["quote", "rewrite_suggestion", "count", "target_register"])
def test_translate_rejects_changed_protected_fields(app_module, monkeypatch, change):
    original = {**REPORT, "annotations": [annotation()]}
    translated = copy.deepcopy(original)
    if change == "count":
        translated["annotations"] = []
    elif change == "target_register":
        translated[change] = "casual"
    else:
        translated["annotations"][0][change] = "altered"
    provider(app_module, monkeypatch, translated)
    assert api(app_module.app, "/translate", {"analysis": original}).status_code == 502
