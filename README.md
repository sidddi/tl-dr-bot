# tl-dr-bot

Bot de Telegram que recibe cualquier URL (artículos, hilos de Twitter/X, blogs), decide si vale la pena leerla, la resume con Claude y la guarda clasificada en tu vault de Obsidian.

## El problema que resuelve

Vas acumulando links durante el día — artículos, hilos de Twitter, posts, blogs. No tienes tiempo de leerlos todos en el momento, y al final se pierden o no sabes si valía la pena guardarlos.

tl-dr-bot actúa como filtro inteligente:
- **¿Vale la pena?** Claude lee el artículo y te dice si aporta algo nuevo o es contenido básico ya cubierto
- **¿Dónde va?** Lo clasifica automáticamente según tus categorías y lo guarda en Obsidian
- **¿Qué dice?** Te da un resumen de 3 bullets para que sepas de qué va sin leerlo entero

Todo desde Telegram, sin abrir el ordenador.

## Cómo funciona

1. Mandas una URL por Telegram
2. El bot fetcha el contenido con [Jina AI Reader](https://r.jina.ai) — funciona con Twitter/X, JavaScript, paywalls básicos
3. Claude analiza el artículo y devuelve: título, resumen en 3 bullets, categoría, conceptos relacionados y si vale la pena leerlo
4. Se guarda un `.md` en tu vault de Obsidian (vía GitHub API) con frontmatter YAML
5. El bot te responde: ✅ si vale la pena, 🗑️ si no

### Categorías

Las categorías son personalizadas por cada usuario con `python setup.py`. Claude propone categorías con nombre y descripción según tus intereses, o puedes definirlas a mano.

`Basura` se añade siempre automáticamente para artículos que no aportan valor.

## Antes de empezar

Necesitas tres cosas:

### 1. API key de Anthropic

Entra en [console.anthropic.com](https://console.anthropic.com) → API Keys → Create Key. Necesitarás añadir créditos (unos pocos euros dan para miles de resúmenes).

### 2. Bot de Telegram

1. Abre Telegram y busca [@BotFather](https://t.me/BotFather)
2. Escribe `/newbot`
3. Ponle un nombre y un username (ej: `mi_tl_dr_bot`)
4. BotFather te dará un token — guárdalo

### 3. Vault de Obsidian en GitHub

El bot escribe las notas directamente en tu repo de Obsidian vía GitHub API. Si aún no tienes el vault en git:

1. Crea un repo en GitHub (puede ser privado)
2. Clónalo y mueve tu vault de Obsidian ahí, o init git dentro del vault:
   ```bash
   cd ~/Documents/ObsidianVault
   git init
   git remote add origin https://github.com/tu-usuario/obsidian.git
   git add . && git commit -m "init"
   git push -u origin main
   ```
3. En Obsidian: Settings → Community Plugins → busca **Obsidian Git** → instálalo para que Obsidian sincronice automáticamente con el repo

Luego crea un **fine-grained token** en GitHub:
GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → New token
Permiso necesario: **Contents → Read and write** (solo sobre el repo del vault)

## Requisitos

- Python 3.9+
- API key de Anthropic
- Bot de Telegram
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
