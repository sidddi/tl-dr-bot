import json
import anthropic
from config import ANTHROPIC_API_KEY, get_categories

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

_SYSTEM_PROMPT_TEMPLATE = """Eres un asistente de investigación. Dado el texto de un artículo, devuelve SOLO un objeto JSON con estos campos:
- title: string — título del artículo
- summary: array de máximo 3 strings — puntos clave concisos en español
- category: uno de {categories} — la categoría más adecuada
- relacionado: array de 2-3 strings — conceptos relevantes como wikilinks de Obsidian, ej: ["Agentes", "RAG", "MCP"]
- vale_la_pena: string — una frase en español: ¿aporta algo nuevo o es contenido básico ya cubierto?
- worth_reading: boolean — true si aporta perspectiva nueva o valor real, false si es básico, repetitivo, superficial o ya conocido

Devuelve solo el objeto JSON sin bloques de código ni texto extra."""


def summarize(text: str, url: str) -> dict:
    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(categories=", ".join(get_categories()))
    user_message = f"URL: {url}\n\nTEXTO:\n{text[:12000]}"

    message = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": user_message}],
        system=system_prompt,
    )

    raw = message.content[0].text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)
