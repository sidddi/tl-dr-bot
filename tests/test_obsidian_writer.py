import pytest
from unittest.mock import patch, MagicMock
from obsidian_writer import write_note


SUMMARY_WORTH_READING = {
    "title": "Cómo funcionan los Agentes de IA",
    "category": "Agents",
    "summary": ["Punto 1", "Punto 2", "Punto 3"],
    "relacionado": ["Agentes", "LLMs"],
    "vale_la_pena": "Muy buen artículo con perspectiva novedosa.",
    "worth_reading": True,
}

SUMMARY_NOT_WORTH = {
    **SUMMARY_WORTH_READING,
    "worth_reading": False,
    "vale_la_pena": "Contenido básico ya cubierto en otros sitios.",
}


def _mock_github(sha=None):
    mock_get = MagicMock()
    mock_get.return_value.status_code = 200 if sha else 404
    if sha:
        mock_get.return_value.json.return_value = {"sha": sha}

    mock_put = MagicMock()
    mock_put.return_value.raise_for_status = MagicMock()

    return mock_get, mock_put


def test_write_note_routes_to_category_folder():
    mock_get, mock_put = _mock_github()

    with patch("obsidian_writer.requests.get", mock_get), \
         patch("obsidian_writer.requests.put", mock_put):
        path = write_note("https://example.com", SUMMARY_WORTH_READING)

    assert "/Agents/" in path


def test_write_note_routes_to_basura_when_not_worth_reading():
    mock_get, mock_put = _mock_github()

    with patch("obsidian_writer.requests.get", mock_get), \
         patch("obsidian_writer.requests.put", mock_put):
        path = write_note("https://example.com", SUMMARY_NOT_WORTH)

    assert "/Basura/" in path


def test_write_note_frontmatter_contains_required_fields():
    mock_get, mock_put = _mock_github()

    with patch("obsidian_writer.requests.get", mock_get), \
         patch("obsidian_writer.requests.put", mock_put):
        write_note("https://example.com", SUMMARY_WORTH_READING)

    import base64
    payload = mock_put.call_args[1]["json"]
    content = base64.b64decode(payload["content"]).decode("utf-8")

    assert 'title: "Cómo funcionan los Agentes de IA"' in content
    assert "category: Agents" in content
    assert 'source: "https://example.com"' in content
    assert "## Resumen" in content
    assert "## Relacionado" in content
    assert "## ¿Vale la pena?" in content


def test_write_note_includes_sha_when_file_exists():
    mock_get, mock_put = _mock_github(sha="abc123")

    with patch("obsidian_writer.requests.get", mock_get), \
         patch("obsidian_writer.requests.put", mock_put):
        write_note("https://example.com", SUMMARY_WORTH_READING)

    payload = mock_put.call_args[1]["json"]
    assert payload["sha"] == "abc123"


def test_write_note_no_sha_when_file_is_new():
    mock_get, mock_put = _mock_github(sha=None)

    with patch("obsidian_writer.requests.get", mock_get), \
         patch("obsidian_writer.requests.put", mock_put):
        write_note("https://example.com", SUMMARY_WORTH_READING)

    payload = mock_put.call_args[1]["json"]
    assert "sha" not in payload
