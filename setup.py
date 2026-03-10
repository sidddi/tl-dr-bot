import base64
import json
import os
import anthropic
import requests

CONFIG_FILE = "config.json"
ENV_FILE = ".env"


def _ask(prompt: str, secret: bool = False) -> str:
    value = input(prompt).strip()
    return value


def _setup_credentials() -> dict:
    print("Necesito tus credenciales para configurar el bot.\n")

    existing = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()

    def ask_with_default(prompt, key):
        current = existing.get(key, "")
        hint = f" [actual: {'*' * 8 + current[-4:] if current else 'no configurado'}]" if current else ""
        raw = input(f"{prompt}{hint}: ").strip()
        return raw if raw else current

    print("1/5 — Token del bot de Telegram (BotFather → /newbot)")
    telegram_token = ask_with_default("  TELEGRAM_TOKEN", "TELEGRAM_TOKEN")

    print("\n2/5 — API key de Anthropic (console.anthropic.com)")
    anthropic_key = ask_with_default("  ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY")

    print("\n3/5 — GitHub Personal Access Token")
    print("       (GitHub → Settings → Developer settings → Fine-grained tokens)")
    print("       Permiso necesario: Contents → Read and write sobre el repo del vault")
    github_token = ask_with_default("  GITHUB_TOKEN", "GITHUB_TOKEN")

    print("\n4/5 — Repositorio de GitHub del vault de Obsidian (ej: usuario/obsidian)")
    github_repo = ask_with_default("  GITHUB_VAULT_REPO", "GITHUB_VAULT_REPO")

    print("\n5/5 — Carpeta base dentro del repo donde guardar las notas (ej: TL-DR)")
    github_base = ask_with_default("  GITHUB_VAULT_BASE_PATH", "GITHUB_VAULT_BASE_PATH")
    if not github_base:
        github_base = "04_Sources"

    return {
        "TELEGRAM_TOKEN": telegram_token,
        "ANTHROPIC_API_KEY": anthropic_key,
        "GITHUB_TOKEN": github_token,
        "GITHUB_VAULT_REPO": github_repo,
        "GITHUB_VAULT_BASE_PATH": github_base,
    }


def _save_env(creds: dict):
    with open(ENV_FILE, "w") as f:
        for k, v in creds.items():
            f.write(f"{k}={v}\n")
    print(f"\nCredenciales guardadas en {ENV_FILE}")


def _propose_categories(interests: str, api_key: str) -> list[dict]:
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""El usuario quiere guardar y clasificar artículos sobre estos temas: {interests}

Propón entre 6 y 8 categorías para organizar sus notas. Devuelve SOLO un array JSON con objetos con estos campos:
- name: string — nombre corto de la categoría (1-2 palabras, sin espacios raros)
- description: string — una frase que explica qué tipo de artículos van aquí y qué los diferencia de otras categorías

Ejemplo de formato:
[
  {{"name": "LLMs", "description": "Modelos de lenguaje: arquitectura, benchmarks, nuevos modelos. No incluye aplicaciones prácticas."}},
  {{"name": "Tools", "description": "Herramientas y apps concretas de IA: interfaces, APIs, plataformas. No incluye los modelos en sí."}}
]

Devuelve solo el array JSON, sin texto extra."""
        }],
    )
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    return json.loads(raw)


def _print_categories(categories: list[dict]):
    print()
    for i, cat in enumerate(categories, 1):
        print(f"  {i}. {cat['name']}: {cat['description']}")
    print()


def _manual_input() -> list[dict]:
    print("\nIntroduce tus categorías una a una. Escribe 'fin' cuando termines.\n")
    categories = []
    while True:
        name = input("  Nombre de la categoría (o 'fin'): ").strip()
        if name.lower() == "fin":
            break
        if not name:
            continue
        description = input(f"  Descripción de '{name}' (qué artículos van aquí): ").strip()
        categories.append({"name": name, "description": description})
        print()
    return categories


def _setup_categories(api_key: str) -> list[dict]:
    print("\n--- Categorías ---\n")

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            existing = json.load(f).get("categories", [])
        if existing:
            print("Categorías actuales:")
            for cat in existing:
                print(f"  - {cat['name']}: {cat['description']}")
            print("\n¿Qué quieres hacer?")
            print("  [k] Mantener las categorías actuales")
            print("  [r] Reemplazarlas con nuevas")
            choice = input("\n> ").strip().lower()
            if choice != "r":
                print("Manteniendo categorías actuales.")
                return existing

    print("¿Sobre qué temas quieres aprender o guardar artículos?")
    print("(ej: inteligencia artificial, startups, diseño de producto, finanzas...)\n")
    interests = input("> ").strip()
    if not interests:
        print("No has introducido nada, usando categorías por defecto.")
        return []

    print("\nGenerando categorías...")
    categories = _propose_categories(interests, api_key)

    while True:
        print("Te propongo estas categorías:")
        _print_categories(categories)

        print("¿Qué quieres hacer?")
        print("  [s] Aceptar estas categorías")
        print("  [n] Generar nuevas propuestas")
        print("  [m] Definirlas a mano")
        choice = input("\n> ").strip().lower()

        if choice == "s":
            break
        elif choice == "n":
            print("\nGenerando nuevas propuestas...")
            categories = _propose_categories(interests, api_key)
        elif choice == "m":
            categories = _manual_input()
            if not categories:
                print("No has introducido ninguna categoría. Volviendo al menú.")
                continue
            break
        else:
            print("Opción no válida. Escribe s, n o m.")

    if not any(c["name"] == "Basura" for c in categories):
        categories.append({
            "name": "Basura",
            "description": "Artículos que no aportan valor: superficiales, repetitivos o irrelevantes."
        })

    return categories


def _create_index(github_token: str, github_repo: str, base_path: str) -> None:
    from obsidian_writer import _INDEX_CONTENT
    path = f"{base_path}/TL-DR Index.md"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json",
    }
    r = requests.get(
        f"https://api.github.com/repos/{github_repo}/contents/{path}",
        headers=headers,
    )
    if r.status_code == 200:
        print("\n  TL-DR Index.md ya existe, no se sobreescribe.")
        return
    encoded = base64.b64encode(_INDEX_CONTENT.encode("utf-8")).decode("utf-8")
    r = requests.put(
        f"https://api.github.com/repos/{github_repo}/contents/{path}",
        headers=headers,
        json={"message": "add: TL-DR Index", "content": encoded},
    )
    r.raise_for_status()
    print("\n  ✓ TL-DR Index.md creado en tu vault de Obsidian.")


def run_setup():
    print("=== tl-dr-bot setup ===\n")

    creds = _setup_credentials()
    _save_env(creds)

    categories = _setup_categories(creds["ANTHROPIC_API_KEY"])

    config = {"categories": categories} if categories else {}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\nCategorías guardadas en {CONFIG_FILE}:")
    for cat in (categories or [{"name": "defaults", "description": "se usarán las categorías por defecto"}]):
        print(f"  - {cat['name']}: {cat['description']}")

    print("\nCreando TL-DR Index.md en tu vault de Obsidian...")
    _create_index(
        creds["GITHUB_TOKEN"],
        creds["GITHUB_VAULT_REPO"],
        creds["GITHUB_VAULT_BASE_PATH"],
    )

    print("\n✓ Setup completado. Ya puedes correr: python main.py")


if __name__ == "__main__":
    run_setup()
