"""Validate dataset structure only; never call a model or score language quality."""
import json
from pathlib import Path

def validate():
    cases = json.loads((Path(__file__).with_name("cases.json")).read_text())
    assert len(cases) == len({c["id"] for c in cases}) == 12
    for case in cases:
        assert case["language"] in {"en", "pt"}
        assert case["context"] in {"academic", "professional", "casual"}
        assert case["expectation"] in {"no_change", "contextual_review"}
        minimum = 50 if case["language"] == "en" else 1
        assert minimum <= len(case["text"].split()) <= 500, case["id"]
        assert case["rationale"] and case["annotation_status"]
    assert {(c["language"], c["context"]) for c in cases if c["expectation"] == "no_change"} == {
        (lang, register) for lang in ["en", "pt"] for register in ["academic", "professional", "casual"]
    }
    return cases

if __name__ == "__main__":
    cases = validate()
    print(f"{len(cases)} cases structurally valid; 6 no-change cases. Model evaluation: NOT RUN.")
