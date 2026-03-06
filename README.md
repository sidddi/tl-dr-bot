# tl-dr-bot

Telegram bot que recibe cualquier URL (artículos, hilos de Twitter/X, blogs), la resume con Claude y guarda la nota en tu vault de Obsidian.

## Qué hace

1. Recibes una URL en Telegram
2. El bot fetcha el contenido con [Jina AI Reader](https://r.jina.ai) (funciona con Twitter, JavaScript, paywalls básicos)
3. Claude analiza el artículo y devuelve: título, resumen en 3 bullets, categoría, conceptos relacionados y si vale la pena leerlo
4. Se guarda un `.md` en tu vault de Obsidian con frontmatter YAML
5. El bot te responde con un mensaje conversacional: ✅ si vale la pena, 🗑️ si no

### Categorías

`Agents` · `MCP` · `LLMs` · `Tools` · `Carrera` · `Tutorials` · `Basura`

Los artículos que no valen la pena se guardan en `Basura/` automáticamente.

## Requisitos

- Python 3.9+
- Token de Telegram Bot ([@BotFather](https://t.me/BotFather))
- API key de Anthropic ([console.anthropic.com](https://console.anthropic.com))
- Ruta local a tu vault de Obsidian

## Instalación

```bash
git clone https://github.com/tu-usuario/tl-dr-bot.git
cd tl-dr-bot

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto:

```env
TELEGRAM_TOKEN=7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-api03-...
OBSIDIAN_VAULT_PATH=/Users/tu-usuario/obsidian/TL-DR
```

## Uso

```bash
source .env  # o exporta las variables manualmente
python main.py
```

Abre Telegram, busca tu bot y mándale cualquier URL.

## Estructura del proyecto

```
tl-dr-bot/
├── main.py            # Bot de Telegram
├── fetcher.py         # Fetching de URLs con Jina AI Reader
├── summarizer.py      # Llamada a Claude API
├── obsidian_writer.py # Escritura de notas en Obsidian
├── config.py          # Variables de entorno
└── requirements.txt
```

## Estructura de notas en Obsidian

```
OBSIDIAN_VAULT_PATH/
├── Agents/
├── MCP/
├── LLMs/
├── Tools/
├── Carrera/
├── Tutorials/
└── Basura/
```

Cada nota incluye frontmatter YAML, resumen en bullets, wikilinks relacionados y valoración de si merece la pena.
