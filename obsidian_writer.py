import re
import base64
from datetime import datetime
import requests
from config import GITHUB_TOKEN, GITHUB_VAULT_REPO, GITHUB_VAULT_BASE_PATH

GITHUB_API = "https://api.github.com"


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


_INDEX_CONTENT = """\
# TL-DR Index

## 📋 Pendents

### 🤖 Agentes
```dataview
TABLE title, tipus, date, source
FROM "TL-DR/Agentes"
WHERE status = "pendent"
SORT date DESC
```

### 📚 Aprendizaje Técnico
```dataview
TABLE title, tipus, date, source
FROM "TL-DR/Aprendizaje Técnico"
WHERE status = "pendent"
SORT date DESC
```

### 📈 Tendencias
```dataview
TABLE title, tipus, date, source
FROM "TL-DR/Tendencias"
WHERE status = "pendent"
SORT date DESC
```

---

## ✅ Llegits
```dataview
TABLE title, category, tipus, date, source
FROM "TL-DR"
WHERE status = "llegit"
SORT date DESC
```
"""


def _ensure_index() -> None:
    path = f"{GITHUB_VAULT_BASE_PATH}/TL-DR Index.md"
    sha = _get_file_sha(path)
    if sha is not None:
        return
    encoded = base64.b64encode(_INDEX_CONTENT.encode("utf-8")).decode("utf-8")
    r = requests.put(
        f"{GITHUB_API}/repos/{GITHUB_VAULT_REPO}/contents/{path}",
        headers=_github_headers(),
        json={"message": "add: TL-DR Index", "content": encoded},
    )
    r.raise_for_status()


def write_note(url: str, summary: dict) -> str:
    _ensure_index()
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
