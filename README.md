# tl-dr-bot

Bot de Telegram que recibe cualquier URL (artículos, hilos de Twitter/X, blogs), la resume con Claude y guarda la nota en tu vault de Obsidian vía GitHub.

## Qué hace

1. Mandas una URL por Telegram
2. El bot fetcha el contenido con [Jina AI Reader](https://r.jina.ai) — funciona con Twitter/X, JavaScript, paywalls básicos
3. Claude analiza el artículo y devuelve: título, resumen en 3 bullets, categoría, conceptos relacionados y si vale la pena leerlo
4. Se guarda un `.md` en tu vault de Obsidian (vía GitHub API) con frontmatter YAML
5. El bot te responde: ✅ si vale la pena, 🗑️ si no

### Categorías

`Agents` · `MCP` · `LLMs` · `Tools` · `Carrera` · `Tutorials` · `Basura`

Los artículos que no valen la pena se guardan en `Basura/` automáticamente.

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

Crea un archivo `.env` en la raíz del proyecto (o configura las variables en Railway):

```env
TELEGRAM_TOKEN=7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-api03-...

# GitHub — el bot escribe las notas directamente en tu vault repo
GITHUB_TOKEN=ghp_...
GITHUB_VAULT_REPO=tu-usuario/tu-vault-repo
GITHUB_VAULT_BASE_PATH=04_Sources   # ruta dentro del repo (opcional, default: 04_Sources)
```

### Cómo obtener el GitHub Token

GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → New token

Permisos necesarios: **Contents** → Read and write (solo en el repo del vault)

## Configuración de categorías

Ejecuta el script de setup para definir tus categorías temáticas:

```bash
python setup.py
```

Te pedirá las categorías separadas por comas (ej: `AI, Producto, Negocios, Tutoriales`). Las guarda en `config.json` (no se sube a git). `Basura` se añade siempre automáticamente como fallback.

Si no ejecutas setup, el bot usa las categorías por defecto: `Agents, MCP, LLMs, Tools, Carrera, Tutorials, Basura`.

## Uso local

> ⚠️ Solo puede haber una instancia corriendo a la vez. Si el bot está en Railway, no lo arranques en local.

```bash
export TELEGRAM_TOKEN=...
export ANTHROPIC_API_KEY=...
export GITHUB_TOKEN=...
export GITHUB_VAULT_REPO=tu-usuario/obsidian
export GITHUB_VAULT_BASE_PATH=TL-DR

python setup.py   # primera vez
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
