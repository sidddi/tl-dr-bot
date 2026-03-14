# tl-dr-bot

Bot de Telegram que recibe cualquier URL (artículos, hilos de Twitter/X, blogs), decide si vale la pena leerla, la resume con Claude y la guarda clasificada en tu vault de Obsidian.

## El problema que resuelve

Vas acumulando links durante el día — artículos, hilos de Twitter, posts, blogs. No tienes tiempo de leerlos todos en el momento, y al final se pierden o no sabes si valía la pena guardarlos.

tl-dr-bot actúa como filtro inteligente:
- **¿Vale la pena?** Claude lee el artículo y te dice si aporta algo nuevo o es contenido básico ya cubierto
- **¿Dónde va?** Lo clasifica automáticamente según tus categorías y lo guarda en Obsidian
- **¿Qué dice?** Te da un resumen de 3 bullets para que sepas de qué va sin leerlo entero
- **¿Ya lo tienes?** Detecta duplicados — si mandas una URL que ya guardaste, te avisa sin volver a procesarla

Todo desde Telegram, sin abrir el ordenador.

## Cómo funciona

1. Mandas una URL por Telegram
2. El bot comprueba si ya está guardada — si es duplicado, te avisa y para aquí
3. Fetcha el contenido con [Jina AI Reader](https://r.jina.ai) — funciona con Twitter/X, JavaScript, paywalls básicos
4. Claude analiza el artículo y devuelve: título, resumen en 3 bullets, categoría, conceptos relacionados, tipo y valoración
5. Se guarda un `.md` en tu vault de Obsidian (vía GitHub API) con frontmatter YAML
6. El bot te responde: ✅ si vale la pena, 🗑️ si no

### Categorías

Las categorías son personalizadas por cada usuario con `python setup.py`. Claude propone categorías con nombre y descripción según tus intereses, o puedes definirlas a mano.

`Basura` se añade siempre automáticamente para artículos que no aportan valor.

### Frontmatter de cada nota

Cada nota guardada en Obsidian incluye estos campos en el YAML:

```yaml
---
title: "Título del artículo"
date: 2026-03-10
category: Agentes
tipus: article        # "article" (lectura rápida) o "tutorial" (requiere práctica)
status: pendent       # cambia a "llegit" cuando lo hayas leído
source: "https://..."
---
```

**Flujo de lectura:** cuando termines de leer un artículo, abre la nota en Obsidian y cambia `status: pendent` a `status: llegit`. El índice se actualiza automáticamente.

### TL-DR Index

Al ejecutar `setup.py` se crea (o actualiza) automáticamente un archivo `TL-DR Index.md` en la raíz de tu carpeta. Contiene una tabla Dataview por categoría con todos los artículos ordenados por estado (`pendent` primero) y fecha.

Requiere el plugin [Dataview](https://github.com/blacksmithgu/obsidian-dataview) instalado en Obsidian.

### Deduplicación

El bot mantiene un archivo `seen_urls.txt` en tu vault con todas las URLs ya procesadas. Si mandas una URL repetida, responde `⚠️ Esta URL ya está guardada en tu vault.` sin volver a fetchear ni consumir créditos de Claude.

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

**2. Categorías** — te pregunta sobre qué temas quieres aprender, Claude propone categorías con nombre y descripción, y puedes aceptarlas, pedir nuevas, o definirlas a mano. Si ya tienes categorías guardadas, te pregunta si quieres mantenerlas o reemplazarlas. Se guardan en `config.json` (no se sube a git).

Las descripciones son clave: Claude las usa para clasificar correctamente cada artículo.

**3. TL-DR Index** — crea automáticamente `TL-DR Index.md` en tu vault con queries Dataview para navegar los artículos pendientes y leídos por categoría.

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

## Newsletter semanal

`newsletter.py` genera un borrador de newsletter para LinkedIn a partir de los artículos que hayas marcado como leídos (`status: llegit`) en la última semana.

```bash
python newsletter.py
```

**Qué hace:**
1. Lee todos los archivos `.md` del repo de Obsidian vía GitHub API
2. Filtra los que tienen `status: llegit` y `date` de los últimos 7 días
3. Agrupa los artículos por categoría con sus resúmenes
4. Llama a Claude para generar el borrador en español, tono natural, sin frases de IA
5. Guarda el borrador en `Newsletter/Newsletter-{YYYY}-W{WW}.md` en el vault
6. Te notifica por Telegram con el nombre del archivo generado

Si no has leído ningún artículo esta semana, te avisa por Telegram sin generar nada.

**Variables de entorno necesarias** (además de las del bot):
- `GITHUB_REPO` — repo en formato `usuario/repo`
- `TELEGRAM_BOT_TOKEN` — token del bot de Telegram
- `TELEGRAM_CHAT_ID` — tu chat ID de Telegram

## Estructura del proyecto

```
tl-dr-bot/
├── main.py            # Bot de Telegram
├── setup.py           # Configuración inicial de categorías
├── newsletter.py      # Generador de newsletter semanal
├── fetcher.py         # Fetching de URLs con Jina AI Reader
├── summarizer.py      # Llamada a Claude API
├── obsidian_writer.py # Escritura de notas en Obsidian vía GitHub API
├── config.py          # Variables de entorno y carga de config.json
└── requirements.txt
```

## Estructura de notas en Obsidian

Las carpetas se crean automáticamente según las categorías que hayas definido en `setup.py`. Por ejemplo, si configuraste `AI`, `Producto` y `Startups`:

```
GITHUB_VAULT_BASE_PATH/
├── AI/
├── Producto/
├── Startups/
├── Basura/           ← siempre presente para artículos descartados
├── TL-DR Index.md    ← índice Dataview generado por setup.py
└── seen_urls.txt     ← registro de URLs ya procesadas (deduplicación)
```

Cada nota incluye frontmatter YAML (título, fecha, categoría, `tipus`, `status`, fuente), resumen en bullets, wikilinks relacionados y valoración de si merece la pena.

Para marcar un artículo como leído, abre la nota en Obsidian y cambia `status: pendent` a `status: llegit`.
