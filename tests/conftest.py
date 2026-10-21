import importlib
from unittest.mock import patch

import pytest


@pytest.fixture
def app_module(monkeypatch):
    # Never load a developer's .env or use an existing provider credential.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with patch("dotenv.load_dotenv"):
        import main
        module = importlib.reload(main)
    return module
