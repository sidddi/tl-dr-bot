import base64
import pytest
from unittest.mock import patch, MagicMock, call
from obsidian_writer import write_note, is_url_seen, mark_url_seen


SUMMARY_WORTH_READING = {
    "title": "Cómo funcionan los Agentes de IA",
    "category": "Agentes",
    "summary": ["Punto 1", "Punto 2", "Punto 3"],
    "relacionado": ["Agentes", "LLMs"],
    "vale_la_pena": "Muy buen artículo con perspectiva novedosa.",
    "worth_reading": True,
    "tipus": "article",
    "status": "pendent",
}

SUMMARY_NOT_WORTH = {
    **SUMMARY_WORTH_READING,
    "worth_reading": False,
    "vale_la_pena": "Contenido básico ya cubierto en otros sitios.",
}


def _make_get(note_sha=None):
    """Return a mock for requests.get that handles note SHA and .seen_urls separately."""
    def side_effect(url, **kwargs):
        m = MagicMock()
        if ".seen_urls" in url:
            m.status_code = 404
        elif note_sha:
            m.status_code = 200
            m.json.return_value = {"sha": note_sha}
        else:
            m.status_code = 404
        return m
    return MagicMock(side_effect=side_effect)


def _make_put():
    mock = MagicMock()
    mock.return_value.raise_for_status = MagicMock()
    return mock


def test_write_note_routes_to_category_folder():
    with patch("obsidian_writer.requests.get", _make_get()), \
         patch("obsidian_writer.requests.put", _make_put()):
        path = write_note("https://example.com", SUMMARY_WORTH_READING)

    assert "/Agentes/" in path


def test_write_note_routes_to_basura_when_not_worth_reading():
    with patch("obsidian_writer.requests.get", _make_get()), \
         patch("obsidian_writer.requests.put", _make_put()):
        path = write_note("https://example.com", SUMMARY_NOT_WORTH)

    assert "/Basura/" in path


def test_write_note_frontmatter_contains_required_fields():
    mock_put = _make_put()

    with patch("obsidian_writer.requests.get", _make_get()), \
         patch("obsidian_writer.requests.put", mock_put):
        write_note("https://example.com", SUMMARY_WORTH_READING)

    payload = mock_put.call_args[1]["json"]
    content = base64.b64decode(payload["content"]).decode("utf-8")

    assert 'title: "Cómo funcionan los Agentes de IA"' in content
    assert "category: Agentes" in content
    assert "tipus: article" in content
    assert "status: pendent" in content
    assert 'source: "https://example.com"' in content
    assert "## Resumen" in content
    assert "## Relacionado" in content
    assert "## ¿Vale la pena?" in content


def test_write_note_includes_sha_when_file_exists():
    mock_put = _make_put()

    with patch("obsidian_writer.requests.get", _make_get(note_sha="abc123")), \
         patch("obsidian_writer.requests.put", mock_put):
        write_note("https://example.com", SUMMARY_WORTH_READING)

    payload = mock_put.call_args[1]["json"]
    assert payload["sha"] == "abc123"


def test_write_note_no_sha_when_file_is_new():
    mock_put = _make_put()

    with patch("obsidian_writer.requests.get", _make_get()), \
         patch("obsidian_writer.requests.put", mock_put):
        write_note("https://example.com", SUMMARY_WORTH_READING)

    payload = mock_put.call_args[1]["json"]
    assert "sha" not in payload


def test_write_note_only_calls_one_put():
    """write_note no longer calls mark_url_seen internally."""
    mock_put = _make_put()

    with patch("obsidian_writer.requests.get", _make_get()), \
         patch("obsidian_writer.requests.put", mock_put):
        write_note("https://example.com/article", SUMMARY_WORTH_READING)

    assert mock_put.call_count == 1


def test_is_url_seen_returns_true_when_url_in_file():
    url = "https://example.com/already-saved"
    encoded = base64.b64encode((url + "\n").encode()).decode()

    mock_get = MagicMock()
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"content": encoded}

    with patch("obsidian_writer.requests.get", mock_get):
        assert is_url_seen(url) is True


def test_is_url_seen_returns_false_when_url_not_in_file():
    encoded = base64.b64encode(b"https://other.com\n").decode()

    mock_get = MagicMock()
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"content": encoded}

    with patch("obsidian_writer.requests.get", mock_get):
        assert is_url_seen("https://example.com/new") is False


def test_is_url_seen_returns_false_when_file_missing():
    mock_get = MagicMock()
    mock_get.return_value.status_code = 404

    with patch("obsidian_writer.requests.get", mock_get):
        assert is_url_seen("https://example.com/new") is False


def test_is_url_seen_returns_false_on_exception():
    mock_get = MagicMock(side_effect=Exception("network error"))

    with patch("obsidian_writer.requests.get", mock_get):
        assert is_url_seen("https://example.com/new") is False


def test_mark_url_seen_writes_url_to_file():
    mock_get = MagicMock()
    mock_get.return_value.status_code = 404
    mock_put = MagicMock()
    mock_put.return_value.status_code = 201
    mock_put.return_value.raise_for_status = MagicMock()

    with patch("obsidian_writer.requests.get", mock_get), \
         patch("obsidian_writer.requests.put", mock_put):
        mark_url_seen("https://example.com/new")

    payload = mock_put.call_args[1]["json"]
    content = base64.b64decode(payload["content"]).decode("utf-8")
    assert "https://example.com/new" in content


def test_mark_url_seen_does_not_raise_on_error():
    mock_get = MagicMock(side_effect=Exception("network error"))

    with patch("obsidian_writer.requests.get", mock_get):
        mark_url_seen("https://example.com/new")  # should not raise
