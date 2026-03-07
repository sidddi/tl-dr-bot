import json
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_VAULT_REPO = os.environ["GITHUB_VAULT_REPO"]       # ej: "sidddi/obsidian"
GITHUB_VAULT_BASE_PATH = os.environ.get("GITHUB_VAULT_BASE_PATH", "04_Sources")

_DEFAULT_CATEGORIES = [
    {"name": "Agents", "description": "Agentes autónomos de IA: arquitecturas, frameworks y casos de uso."},
    {"name": "MCP", "description": "Model Context Protocol: herramientas, servidores y integraciones."},
    {"name": "LLMs", "description": "Modelos de lenguaje: arquitectura, benchmarks y nuevos modelos."},
    {"name": "Tools", "description": "Herramientas y plataformas prácticas de IA: APIs, interfaces y servicios."},
    {"name": "Carrera", "description": "Desarrollo profesional, trabajo en IA, oportunidades y tendencias del sector."},
    {"name": "Tutorials", "description": "Guías paso a paso y contenido didáctico con ejemplos prácticos."},
    {"name": "Basura", "description": "Artículos que no aportan valor: superficiales, repetitivos o irrelevantes."},
]


def get_categories() -> list[dict]:
    if os.path.exists("config.json"):
        with open("config.json") as f:
            data = json.load(f)
        categories = data.get("categories", _DEFAULT_CATEGORIES)
    elif os.environ.get("CATEGORIES"):
        # Formato simple desde env var: solo nombres, sin descripción
        categories = [
            {"name": c.strip(), "description": ""}
            for c in os.environ["CATEGORIES"].split(",") if c.strip()
        ]
    else:
        categories = _DEFAULT_CATEGORIES

    if not any(c["name"] == "Basura" for c in categories):
        categories.append({
            "name": "Basura",
            "description": "Artículos que no aportan valor: superficiales, repetitivos o irrelevantes."
        })

    return categories
