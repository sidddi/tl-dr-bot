import json
import os
import anthropic

CONFIG_FILE = "config.json"


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


def run_setup():
    print("=== tl-dr-bot setup ===\n")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Necesitas exportar ANTHROPIC_API_KEY antes de correr setup.py")
        return

    print("¿Sobre qué temas quieres aprender o guardar artículos?")
    print("(ej: inteligencia artificial, startups, diseño de producto, finanzas...)\n")
    interests = input("> ").strip()
    if not interests:
        print("No has introducido nada. Saliendo.")
        return

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

    # Siempre añadir Basura al final
    if not any(c["name"] == "Basura" for c in categories):
        categories.append({
            "name": "Basura",
            "description": "Artículos que no aportan valor: superficiales, repetitivos o irrelevantes."
        })

    config = {"categories": categories}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\nGuardado en {CONFIG_FILE}:")
    for cat in categories:
        print(f"  - {cat['name']}: {cat['description']}")
    print("\nYa puedes correr: python main.py")


if __name__ == "__main__":
    run_setup()
