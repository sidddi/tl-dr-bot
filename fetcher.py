import requests

JINA_BASE = "https://r.jina.ai/"
HEADERS = {"Accept": "text/plain"}


def fetch_article(url: str) -> str:
    response = requests.get(f"{JINA_BASE}{url}", headers=HEADERS, timeout=30)
    response.raise_for_status()
    text = response.text.strip()
    if not text:
        raise ValueError("Jina no pudo extraer contenido de la URL.")
    return text
