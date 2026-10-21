import runpy
from pathlib import Path

def test_evaluation_case_structure():
    namespace = runpy.run_path(str(Path(__file__).parents[1] / "evaluation/validate_cases.py"))
    assert len(namespace["validate"]()) == 12
