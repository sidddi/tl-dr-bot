"""Generate a weekly LinkedIn newsletter draft from Obsidian articles marked as read.

Usage:
    python newsletter.py
"""

import os
import base64
from datetime import date
import requests
import anthropic
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO = os.environ["GITHUB_REPO"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

GITHUB_API = "https://api.github.com"
_GITHUB_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


def _send_telegram(message: str) -> None:
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
    )


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    fm_text = content[3:end].strip()
    body = content[end + 3:].strip()
    fm = {}
    for line in fm_text.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip().strip('"')
    return fm, body


def _list_markdown_files() -> list[str]:
    repo_r = requests.get(f"{GITHUB_API}/repos/{GITHUB_REPO}", headers=_GITHUB_HEADERS)
    repo_r.raise_for_status()
    default_branch = repo_r.json()["default_branch"]

    tree_r = requests.get(
        f"{GITHUB_API}/repos/{GITHUB_REPO}/git/trees/{default_branch}?recursive=1",
        headers=_GITHUB_HEADERS,
    )
    tree_r.raise_for_status()
    return [
        item["path"]
        for item in tree_r.json().get("tree", [])
        if item["type"] == "blob" and item["path"].endswith(".md")
    ]


def _fetch_file(path: str) -> str:
    r = requests.get(
        f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}",
        headers=_GITHUB_HEADERS,
    )
    r.raise_for_status()
    return base64.b64decode(r.json()["content"]).decode("utf-8")


def _within_last_7_days(date_str: str) -> bool:
    try:
        return (date.today() - date.fromisoformat(date_str)).days <= 7
    except ValueError:
        return False


def _collect_articles() -> list[dict]:
    articles = []
    for path in _list_markdown_files():
        if any(skip in path for skip in ("Newsletter", "TL-DR Index", "seen_urls")):
            continue
        try:
            content = _fetch_file(path)
        except Exception:
            continue
        fm, body = _parse_frontmatter(content)
        if fm.get("status") != "llegit":
            continue
        article_date = fm.get("date", "")
        if not _within_last_7_days(article_date):
            continue
        articles.append({
            "title": fm.get("title", path.split("/")[-1].replace(".md", "")),
            "category": fm.get("category") or fm.get("categoria", "General"),
            "date": article_date,
            "body": body,
        })
    return articles


def _build_prompt(articles: list[dict]) -> str:
    by_category: dict[str, list[dict]] = {}
    for a in articles:
        by_category.setdefault(a["category"], []).append(a)

    lines = ["Estos son los artículos que he leído esta semana, agrupados por categoría:\n"]
    for category, items in by_category.items():
        lines.append(f"## {category}")
        for item in items:
            lines.append(f"**{item['title']}** ({item['date']})")
            lines.append(item["body"])
            lines.append("")
    lines.append(
        "Escribe un borrador de newsletter semanal para LinkedIn en español, "
        "basándote en estos artículos. Debe tener una introducción breve, "
        "secciones por categoría con los puntos más relevantes, y un cierre."
    )
    return "\n".join(lines)


def _generate_draft(articles: list[dict]) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=(
            "You are a LinkedIn content creator. Write in a natural, human tone. "
            "No em-dashes. No AI-sounding phrases. "
            "Audience: IT professionals and decision-makers."
        ),
        messages=[{"role": "user", "content": _build_prompt(articles)}],
    )
    return message.content[0].text


def _save_draft(draft: str, year: int, week: int, article_count: int) -> str:
    filename = f"Newsletter-{year}-W{week:02d}.md"
    path = f"Newsletter/{filename}"
    content = (
        f"---\n"
        f"date: {date.today().isoformat()}\n"
        f"week: {year}-W{week:02d}\n"
        f"articles: {article_count}\n"
        f"---\n\n"
        f"{draft}"
    )
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    payload = {"message": f"add: newsletter {year}-W{week:02d}", "content": encoded}

    existing = requests.get(
        f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}", headers=_GITHUB_HEADERS
    )
    if existing.status_code == 200:
        payload["sha"] = existing.json()["sha"]

    requests.put(
        f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}",
        headers=_GITHUB_HEADERS,
        json=payload,
    ).raise_for_status()
    return filename


def main() -> None:
    year, week, _ = date.today().isocalendar()

    try:
        articles = _collect_articles()
    except Exception as e:
        _send_telegram(f"❌ Newsletter error: could not read Obsidian vault ({e})")
        return

    if not articles:
        _send_telegram("No articles read this week, newsletter not generated.")
        return

    try:
        draft = _generate_draft(articles)
    except Exception as e:
        _send_telegram(f"❌ Newsletter error: could not generate draft ({e})")
        return

    try:
        filename = _save_draft(draft, year, week, len(articles))
    except Exception as e:
        _send_telegram(f"❌ Newsletter error: could not save draft ({e})")
        return

    _send_telegram(f"✅ Newsletter draft generated: {filename}")


if __name__ == "__main__":
    main()
