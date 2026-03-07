# tl-dr-bot

Bot de Telegram que recibe cualquier URL (artículos, hilos de Twitter/X, blogs), la resume con Claude y guarda la nota en tu vault de Obsidian vía GitHub.

## Qué hace

1. Mandas una URL por Telegram
2. El bot fetcha el contenido con [Jina AI Reader](https://r.jina.ai) — funciona con Twitter/X, JavaScript, paywalls básicos
3. Claude analiza el artículo y devuelve: título, resumen en 3 bullets, categoría, conceptos relacionados y si vale la pena leerlo
4. Se guarda un `.md` en tu vault de Obsidian (vía GitHub API) con frontmatter YAML
5. El bot te responde: ✅ si vale la pena, 🗑️ si no

### Categorías

Las categorías son personalizadas por cada usuario con `python setup.py`. Claude propone categorías con nombre y descripción según tus intereses, o puedes definirlas a mano.

`Basura` se añade siempre automáticamente para artículos que no aportan valor.

## Requisitos

- Python 3.9+
- Token de Telegram Bot ([@BotFather](https://t.me/BotFather))
- API key de Anthropic ([console.anthropic.com](https://console.anthropic.com))
- Repo de GitHub con tu vault de Obsidian

## Instalación

```bash
git clone https://github.com/sidddi/tl-dr-bot.git
cd tl-dr-bot

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuración

Ejecuta el script de setup — te guía paso a paso por todo:

```bash
python setup.py
```

El setup hace dos cosas:

**1. Credenciales** — te pide las 5 variables necesarias y las guarda en `.env` (no se sube a git):
- `TELEGRAM_TOKEN` — token del bot (BotFather → `/newbot`)
- `ANTHROPIC_API_KEY` — API key de Anthropic
- `GITHUB_TOKEN` — fine-grained token con permiso **Contents → Read and write** sobre el repo del vault
- `GITHUB_VAULT_REPO` — repo de Obsidian (ej: `usuario/obsidian`)
- `GITHUB_VAULT_BASE_PATH` — carpeta base dentro del repo (ej: `TL-DR`)

**2. Categorías** — te pregunta sobre qué temas quieres aprender, Claude propone 6-8 categorías con nombre y descripción, y puedes aceptarlas, pedir nuevas, o definirlas a mano. Se guardan en `config.json` (no se sube a git).

Las descripciones son clave: Claude las usa para clasificar correctamente cada artículo.

## Uso local

> ⚠️ Solo puede haber una instancia corriendo a la vez. Si el bot está en Railway, no lo arranques en local.

```bash
python setup.py   # primera vez (o para cambiar configuración)
python main.py
```

## Deploy en Railway

1. Entra en [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
2. Selecciona `tl-dr-bot`
3. En Variables, añade las 5 variables de entorno obligatorias
4. Opcionalmente añade `CATEGORIES=AI,Producto,Negocios` para categorías custom (sin `config.json`, Railway usa esta variable o los defaults)
5. Railway arranca `python main.py` automáticamente

El bot queda corriendo 24/7 sin necesitar tu ordenador.

Abre Telegram, busca tu bot y mándale cualquier URL.

## Estructura del proyecto

```
tl-dr-bot/
├── main.py            # Bot de Telegram
├── setup.py           # Configuración inicial de categorías
├── fetcher.py         # Fetching de URLs con Jina AI Reader
├── summarizer.py      # Llamada a Claude API
├── obsidian_writer.py # Escritura de notas en Obsidian vía GitHub API
├── config.py          # Variables de entorno y carga de config.json
└── requirements.txt
```

## Estructura de notas en Obsidian

```
GITHUB_VAULT_BASE_PATH/
├── Agents/
├── MCP/
├── LLMs/
├── Tools/
├── Carrera/
├── Tutorials/
└── Basura/
```

Cada nota incluye frontmatter YAML, resumen en bullets, wikilinks relacionados y valoración de si merece la pena.
