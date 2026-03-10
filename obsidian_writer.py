import re
import base64
import logging
from datetime import datetime
import requests
from config import GITHUB_TOKEN, GITHUB_VAULT_REPO, GITHUB_VAULT_BASE_PATH, get_categories

GITHUB_API = "https://api.github.com"
logger = logging.getLogger(__name__)


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")[:80]


def _github_headers() -> dict:
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


def _get_file_sha(path: str) -> str | None:
    r = requests.get(
        f"{GITHUB_API}/repos/{GITHUB_VAULT_REPO}/contents/{path}",
        headers=_github_headers(),
    )
    if r.status_code == 200:
        return r.json().get("sha")
    return None


_SEEN_URLS_PATH = f"{GITHUB_VAULT_BASE_PATH}/.seen_urls"


def is_url_seen(url: str) -> bool:
    try:
        r = requests.get(
            f"{GITHUB_API}/repos/{GITHUB_VAULT_REPO}/contents/{_SEEN_URLS_PATH}",
            headers=_github_headers(),
        )
        logger.info("is_url_seen: GET %s → %d", _SEEN_URLS_PATH, r.status_code)
        if r.status_code != 200:
            return False
        content = base64.b64decode(r.json()["content"]).decode("utf-8")
        found = url in content.splitlines()
        logger.info("is_url_seen: url=%s found=%s", url, found)
        return found
    except Exception as e:
        logger.error("is_url_seen error: %s", e)
        return False


def mark_url_seen(url: str) -> None:
    try:
        r = requests.get(
            f"{GITHUB_API}/repos/{GITHUB_VAULT_REPO}/contents/{_SEEN_URLS_PATH}",
            headers=_github_headers(),
        )
        if r.status_code == 200:
            existing = base64.b64decode(r.json()["content"]).decode("utf-8")
            sha = r.json()["sha"]
        else:
            existing = ""
            sha = None

        new_content = (existing.rstrip("\n") + "\n" + url + "\n").lstrip("\n")
        encoded = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")
        payload = {"message": "track: seen url", "content": encoded}
        if sha:
            payload["sha"] = sha
        resp = requests.put(
            f"{GITHUB_API}/repos/{GITHUB_VAULT_REPO}/contents/{_SEEN_URLS_PATH}",
            headers=_github_headers(),
            json=payload,
        )
        resp.raise_for_status()
        logger.info("mark_url_seen: saved %s (status %d)", url, resp.status_code)
    except Exception as e:
        logger.error("mark_url_seen failed for %s: %s", url, e)


def _build_index_content(base_path: str) -> str:
    categories = [c for c in get_categories() if c["name"] != "Basura"]
    sections = []
    for cat in categories:
        name = cat["name"]
        sections.append(
            f'## {name}\n'
            f'```dataview\n'
            f'TABLE title, tipus, status, date, source\n'
            f'FROM "{base_path}/{name}"\n'
            f'SORT status ASC, date DESC\n'
            f'```'
        )
    return "# TL-DR Index\n\n" + "\n\n".join(sections) + "\n"


def write_note(url: str, summary: dict) -> str:
    title = summary.get("title", "Untitled")
    category = summary.get("category", "General")
    bullets = summary.get("summary", [])
    relacionado = summary.get("relacionado", [])
    vale_la_pena = summary.get("vale_la_pena", "")
    worth_reading = summary.get("worth_reading", True)
    tipus = summary.get("tipus", "article")
    status = summary.get("status", "pendent")
    date_str = datetime.now().strftime("%Y-%m-%d")

    frontmatter = f"""---
title: "{title}"
date: {date_str}
category: {category}
tipus: {tipus}
status: {status}
source: "{url}"
---
"""

    bullets_md = "\n".join(f"- {b}" for b in bullets)
    wikilinks = " ".join(f"[[{r}]]" for r in relacionado)

    body = f"""## Resumen

{bullets_md}

## Relacionado

{wikilinks}

## ¿Vale la pena?

{vale_la_pena}
"""

    content = frontmatter + "\n" + body
    subfolder = category if worth_reading else "Basura"
    filename = f"{date_str}-{_slugify(title)}.md"
    path = f"{GITHUB_VAULT_BASE_PATH}/{subfolder}/{filename}"

    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    sha = _get_file_sha(path)

    payload = {
        "message": f"add: {title}",
        "content": encoded,
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(
        f"{GITHUB_API}/repos/{GITHUB_VAULT_REPO}/contents/{path}",
        headers=_github_headers(),
        json=payload,
    )
    r.raise_for_status()

    return path
