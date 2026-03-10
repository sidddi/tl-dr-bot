import base64
import pytest
from unittest.mock import patch, MagicMock


_MOCK_CATEGORIES = [
    {"name": "Agentes", "description": "..."},
    {"name": "Aprendizaje Técnico", "description": "..."},
    {"name": "Tendencias", "description": "..."},
    {"name": "Basura", "description": "..."},
]


def _mock_get(status_code: int, sha: str = None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = {"sha": sha} if sha else {}
    return mock


def test_create_index_creates_file_when_not_exists():
    mock_get = MagicMock(return_value=_mock_get(404))
    mock_put = MagicMock()
    mock_put.return_value.raise_for_status = MagicMock()

    with patch("setup.requests.get", mock_get), \
         patch("setup.requests.put", mock_put), \
         patch("obsidian_writer.get_categories", return_value=_MOCK_CATEGORIES):
        from setup import _create_index
        _create_index("fake-token", "user/repo", "TL-DR")

    mock_put.assert_called_once()
    mock_put.return_value.raise_for_status.assert_called_once()


def test_create_index_overwrites_if_already_exists():
    mock_get = MagicMock(return_value=_mock_get(200, sha="existing-sha"))
    mock_put = MagicMock()
    mock_put.return_value.raise_for_status = MagicMock()

    with patch("setup.requests.get", mock_get), \
         patch("setup.requests.put", mock_put), \
         patch("obsidian_writer.get_categories", return_value=_MOCK_CATEGORIES):
        from setup import _create_index
        _create_index("fake-token", "user/repo", "TL-DR")

    mock_put.assert_called_once()
    payload = mock_put.call_args[1]["json"]
    assert payload["sha"] == "existing-sha"


def test_create_index_uses_correct_path():
    mock_get = MagicMock(return_value=_mock_get(404))
    mock_put = MagicMock()
    mock_put.return_value.raise_for_status = MagicMock()

    with patch("setup.requests.get", mock_get), \
         patch("setup.requests.put", mock_put), \
         patch("obsidian_writer.get_categories", return_value=_MOCK_CATEGORIES):
        from setup import _create_index
        _create_index("fake-token", "user/repo", "TL-DR")

    called_url = mock_get.call_args[0][0]
    assert "TL-DR/TL-DR%20Index.md" in called_url or "TL-DR Index.md" in called_url


def test_create_index_content_includes_dataview_queries():
    mock_get = MagicMock(return_value=_mock_get(404))
    mock_put = MagicMock()
    mock_put.return_value.raise_for_status = MagicMock()

    with patch("setup.requests.get", mock_get), \
         patch("setup.requests.put", mock_put), \
         patch("obsidian_writer.get_categories", return_value=_MOCK_CATEGORIES):
        from setup import _create_index
        _create_index("fake-token", "user/repo", "TL-DR")

    payload = mock_put.call_args[1]["json"]
    content = base64.b64decode(payload["content"]).decode("utf-8")

    assert "dataview" in content
    assert "TL-DR/Agentes" in content
    assert "TL-DR/Aprendizaje Técnico" in content
    assert "TL-DR/Tendencias" in content
    # Basura should not appear as a section
    assert "TL-DR/Basura" not in content


def test_create_index_excludes_basura_section():
    mock_get = MagicMock(return_value=_mock_get(404))
    mock_put = MagicMock()
    mock_put.return_value.raise_for_status = MagicMock()

    with patch("setup.requests.get", mock_get), \
         patch("setup.requests.put", mock_put), \
         patch("obsidian_writer.get_categories", return_value=_MOCK_CATEGORIES):
        from setup import _create_index
        _create_index("fake-token", "user/repo", "TL-DR")

    payload = mock_put.call_args[1]["json"]
    content = base64.b64decode(payload["content"]).decode("utf-8")
    assert "## Basura" not in content
