import json
import pytest
from unittest.mock import patch, MagicMock
from summarizer import summarize


MOCK_SUMMARY = {
    "title": "Introducción a los Agentes de IA",
    "summary": ["Los agentes pueden tomar decisiones autónomas.", "Usan LLMs como motor de razonamiento.", "El ecosistema de herramientas crece rápido."],
    "category": "Agentes",
    "relacionado": ["Agentes", "LLMs", "RAG"],
    "vale_la_pena": "Aporta una visión clara del estado actual de los agentes.",
    "worth_reading": True,
    "tipus": "article",
    "status": "pendent",
}


def _mock_claude_response(content: str):
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=content)]
    return mock_message


def test_summarize_returns_parsed_dict():
    with patch("summarizer._client.messages.create", return_value=_mock_claude_response(json.dumps(MOCK_SUMMARY))):
        result = summarize("Texto del artículo", "https://example.com")

    assert result["title"] == "Introducción a los Agentes de IA"
    assert result["worth_reading"] is True
    assert len(result["summary"]) == 3


def test_summarize_handles_json_code_block():
    raw = "```json\n" + json.dumps(MOCK_SUMMARY) + "\n```"
    with patch("summarizer._client.messages.create", return_value=_mock_claude_response(raw)):
        result = summarize("Texto del artículo", "https://example.com")

    assert result["category"] == "Agentes"


def test_summarize_prompt_includes_category_descriptions():
    captured = {}

    def fake_create(**kwargs):
        captured["system"] = kwargs.get("system", "")
        return _mock_claude_response(json.dumps(MOCK_SUMMARY))

    custom_cats = [
        {"name": "AI", "description": "Todo sobre inteligencia artificial."},
        {"name": "Basura", "description": "No vale la pena."},
    ]

    with patch("summarizer._client.messages.create", side_effect=fake_create):
        with patch("summarizer.get_categories", return_value=custom_cats):
            summarize("Texto", "https://example.com")

    assert "AI: Todo sobre inteligencia artificial." in captured["system"]
    assert "Basura: No vale la pena." in captured["system"]


def test_summarize_truncates_text_to_12000_chars():
    captured = {}
    long_text = "a" * 20000

    def fake_create(**kwargs):
        captured["messages"] = kwargs.get("messages", [])
        return _mock_claude_response(json.dumps(MOCK_SUMMARY))

    with patch("summarizer._client.messages.create", side_effect=fake_create):
        summarize(long_text, "https://example.com")

    user_content = captured["messages"][0]["content"]
    assert len(user_content) < 13000


def test_summarize_returns_status_pendent():
    with patch("summarizer._client.messages.create", return_value=_mock_claude_response(json.dumps(MOCK_SUMMARY))):
        result = summarize("Texto del artículo", "https://example.com")

    assert "status" in result
    assert result["status"] == "pendent"


def test_summarize_returns_valid_tipus():
    with patch("summarizer._client.messages.create", return_value=_mock_claude_response(json.dumps(MOCK_SUMMARY))):
        result = summarize("Texto del artículo", "https://example.com")

    assert "tipus" in result
    assert result["tipus"] in ("article", "tutorial")


def test_summarize_tipus_tutorial():
    mock = {**MOCK_SUMMARY, "tipus": "tutorial"}
    with patch("summarizer._client.messages.create", return_value=_mock_claude_response(json.dumps(mock))):
        result = summarize("Texto del artículo", "https://example.com")

    assert result["tipus"] == "tutorial"
    assert result["tipus"] in ("article", "tutorial")


def test_summarize_prompt_includes_tipus_and_status_fields():
    captured = {}

    def fake_create(**kwargs):
        captured["system"] = kwargs.get("system", "")
        return _mock_claude_response(json.dumps(MOCK_SUMMARY))

    with patch("summarizer._client.messages.create", side_effect=fake_create):
        summarize("Texto", "https://example.com")

    assert "tipus" in captured["system"]
    assert "status" in captured["system"]
    assert "pendent" in captured["system"]
