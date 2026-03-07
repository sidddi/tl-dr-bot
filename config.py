import json
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_VAULT_REPO = os.environ["GITHUB_VAULT_REPO"]       # ej: "sidddi/obsidian"
GITHUB_VAULT_BASE_PATH = os.environ.get("GITHUB_VAULT_BASE_PATH", "04_Sources")

_DEFAULT_CATEGORIES = ["Agents", "MCP", "LLMs", "Tools", "Carrera", "Tutorials", "Basura"]


def get_categories() -> list[str]:
    if os.path.exists("config.json"):
        with open("config.json") as f:
            data = json.load(f)
        categories = data.get("categories", _DEFAULT_CATEGORIES)
    else:
        categories = _DEFAULT_CATEGORIES

    if "Basura" not in categories:
        categories.append("Basura")

    return categories
