import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CATEGORIES = ["Agents", "MCP", "LLMs", "Tools", "Carrera", "Tutorials"]


def run_setup():
    print("=== tl-dr-bot setup ===\n")

    existing = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            existing = json.load(f)
        print(f"Config existing found at {CONFIG_FILE}. Press Enter to keep current values.\n")

    print(f"Default categories: {', '.join(DEFAULT_CATEGORIES)}")
    raw = input("Enter your categories (comma-separated) or press Enter for defaults: ").strip()

    if raw:
        categories = [c.strip() for c in raw.split(",") if c.strip()]
    elif existing.get("categories"):
        categories = existing["categories"]
    else:
        categories = DEFAULT_CATEGORIES

    if "Basura" not in categories:
        categories.append("Basura")

    config = {**existing, "categories": categories}

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to {CONFIG_FILE}:")
    print(f"  categories: {', '.join(categories)}")
    print("\nYou can now run: python main.py")


if __name__ == "__main__":
    run_setup()
