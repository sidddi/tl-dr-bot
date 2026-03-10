import json
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_VAULT_REPO = os.environ["GITHUB_VAULT_REPO"]       # ej: "sidddi/obsidian"
GITHUB_VAULT_BASE_PATH = os.environ.get("GITHUB_VAULT_BASE_PATH", "04_Sources")

_DEFAULT_CATEGORIES = [
    {"name": "Agentes", "description": "Sistemas de IA autónomos, agentes multi-step, MCP, RAG, flujos de razonamiento automatizado y arquitecturas agentic. Incluye frameworks como LangGraph, AutoGen, CrewAI. No incluye modelos base ni herramientas genéricas."},
    {"name": "Aprendizaje Técnico", "description": "Tutoriales, guías prácticas y recursos educativos sobre técnicas concretas de IA: prompt engineering, RAG, embeddings, fine-tuning, observabilidad. Incluye tanto artículos de lectura rápida como tutoriales que requieren tiempo de práctica. No incluye noticias de industria ni investigación académica."},
    {"name": "Tendencias", "description": "Noticias relevantes sobre el sector IA, lanzamientos de productos, estrategia de empresas y movimientos del mercado. No incluye análisis técnicos profundos ni tutoriales."},
    {"name": "Basura", "description": "Artículos superficiales, repetitivos, clickbait o irrelevantes."},
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
