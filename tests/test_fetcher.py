import pytest
from unittest.mock import patch, MagicMock
from fetcher import fetch_article


def test_fetch_article_returns_text_on_success():
    mock_response = MagicMock()
    mock_response.text = "  Este es el contenido del artículo.  "
    mock_response.raise_for_status = MagicMock()

    with patch("fetcher.requests.get", return_value=mock_response):
        result = fetch_article("https://example.com/article")

    assert result == "Este es el contenido del artículo."


def test_fetch_article_prepends_jina_base_url():
    mock_response = MagicMock()
    mock_response.text = "contenido"
    mock_response.raise_for_status = MagicMock()

    with patch("fetcher.requests.get", return_value=mock_response) as mock_get:
        fetch_article("https://example.com/article")
        called_url = mock_get.call_args[0][0]

    assert called_url == "https://r.jina.ai/https://example.com/article"


def test_fetch_article_raises_on_empty_response():
    mock_response = MagicMock()
    mock_response.text = "   "
    mock_response.raise_for_status = MagicMock()

    with patch("fetcher.requests.get", return_value=mock_response):
        with pytest.raises(ValueError, match="Jina"):
            fetch_article("https://example.com/article")


def test_fetch_article_raises_on_http_error():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")

    with patch("fetcher.requests.get", return_value=mock_response):
        with pytest.raises(Exception):
            fetch_article("https://example.com/article")
