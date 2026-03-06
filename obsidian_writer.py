import os
import re
from datetime import datetime
from config import OBSIDIAN_VAULT_PATH


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")[:80]


def write_note(url: str, summary: dict) -> str:
    title = summary.get("title", "Untitled")
    category = summary.get("category", "General")
    bullets = summary.get("summary", [])
    relacionado = summary.get("relacionado", [])
    vale_la_pena = summary.get("vale_la_pena", "")
    worth_reading = summary.get("worth_reading", True)
    date_str = datetime.now().strftime("%Y-%m-%d")

    frontmatter = f"""---
title: "{title}"
date: {date_str}
category: {category}
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

    subfolder = category if worth_reading else "Basura"  # always Basura if not worth reading
    folder = os.path.join(OBSIDIAN_VAULT_PATH, subfolder)
    os.makedirs(folder, exist_ok=True)
    filename = f"{date_str}-{_slugify(title)}.md"
    filepath = os.path.join(folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath
