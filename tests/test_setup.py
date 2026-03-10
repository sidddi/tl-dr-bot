import os
import pytest
from unittest.mock import patch, MagicMock


def _mock_github_get(status_code: int):
    mock = MagicMock()
    mock.status_code = status_code
    return mock


def _mock_github_put():
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    return mock


def test_create_index_creates_file_when_not_exists():
    mock_get = MagicMock(return_value=_mock_github_get(404))
    mock_put_fn = MagicMock()
    mock_put_fn.return_value.raise_for_status = MagicMock()

    with patch("setup.requests.get", mock_get), \
         patch("setup.requests.put", mock_put_fn):
        from setup import _create_index
        _create_index("fake-token", "user/repo", "TL-DR")

    mock_put_fn.assert_called_once()
    mock_put_fn.return_value.raise_for_status.assert_called_once()


def test_create_index_skips_if_already_exists():
    mock_get = MagicMock(return_value=_mock_github_get(200))
    mock_put = MagicMock()

    with patch("setup.requests.get", mock_get), \
         patch("setup.requests.put", mock_put):
        from setup import _create_index
        _create_index("fake-token", "user/repo", "TL-DR")

    mock_put.assert_not_called()


def test_create_index_uses_correct_path():
    mock_get = MagicMock(return_value=_mock_github_get(404))
    mock_put = MagicMock()
    mock_put.return_value.raise_for_status = MagicMock()

    with patch("setup.requests.get", mock_get), \
         patch("setup.requests.put", mock_put):
        from setup import _create_index
        _create_index("fake-token", "user/repo", "TL-DR")

    called_url = mock_get.call_args[0][0]
    assert "TL-DR/TL-DR%20Index.md" in called_url or "TL-DR Index.md" in called_url


def test_create_index_content_includes_dataview_queries():
    import base64
    mock_get = MagicMock(return_value=_mock_github_get(404))
    mock_put = MagicMock()
    mock_put.return_value.raise_for_status = MagicMock()

    with patch("setup.requests.get", mock_get), \
         patch("setup.requests.put", mock_put):
        from setup import _create_index
        _create_index("fake-token", "user/repo", "TL-DR")

    payload = mock_put.call_args[1]["json"]
    content = base64.b64decode(payload["content"]).decode("utf-8")

    assert "dataview" in content
    assert 'status = "pendent"' in content
    assert 'status = "llegit"' in content
    assert "TL-DR/Agentes" in content
    assert "TL-DR/Aprendizaje Técnico" in content
    assert "TL-DR/Tendencias" in content
