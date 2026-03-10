import json
import os
import pathlib
import pytest
from unittest.mock import patch


def get_config_categories():
    # Re-import to avoid module caching issues
    import importlib
    import config
    importlib.reload(config)
    return config.get_categories()


def test_get_categories_returns_defaults_when_no_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CATEGORIES", raising=False)

    from config import get_categories, _DEFAULT_CATEGORIES
    cats = get_categories()
    assert cats == _DEFAULT_CATEGORIES


def test_get_categories_loads_from_config_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CATEGORIES", raising=False)

    custom = [
        {"name": "AI", "description": "Inteligencia artificial en general."},
        {"name": "Producto", "description": "Diseño y estrategia de producto."},
    ]
    (tmp_path / "config.json").write_text(json.dumps({"categories": custom}))

    from config import get_categories
    cats = get_categories()
    assert cats[0]["name"] == "AI"
    assert cats[1]["name"] == "Producto"


def test_get_categories_adds_basura_if_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CATEGORIES", raising=False)

    custom = [{"name": "AI", "description": "Inteligencia artificial."}]
    (tmp_path / "config.json").write_text(json.dumps({"categories": custom}))

    from config import get_categories
    cats = get_categories()
    names = [c["name"] for c in cats]
    assert "Basura" in names


def test_get_categories_does_not_duplicate_basura(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CATEGORIES", raising=False)

    custom = [
        {"name": "AI", "description": "IA en general."},
        {"name": "Basura", "description": "No vale la pena."},
    ]
    (tmp_path / "config.json").write_text(json.dumps({"categories": custom}))

    from config import get_categories
    cats = get_categories()
    assert [c["name"] for c in cats].count("Basura") == 1


def test_get_categories_from_env_var(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CATEGORIES", "AI, Producto, Startups")

    from config import get_categories
    cats = get_categories()
    names = [c["name"] for c in cats]
    assert "AI" in names
    assert "Producto" in names
    assert "Startups" in names
    assert "Basura" in names  # añadida automáticamente


def test_config_json_has_required_categories():
    config_path = pathlib.Path(__file__).parent.parent / "config.json"
    assert config_path.exists(), "config.json not found"

    data = json.loads(config_path.read_text())
    categories = data.get("categories", [])
    names = [c["name"] for c in categories]

    required = {"Agentes", "Aprendizaje Técnico", "Tendencias", "Basura"}
    assert required == set(names), f"Expected exactly {required}, got {set(names)}"


def test_config_json_all_categories_have_description():
    config_path = pathlib.Path(__file__).parent.parent / "config.json"
    data = json.loads(config_path.read_text())

    for cat in data["categories"]:
        assert cat.get("description", "").strip(), f"Category '{cat['name']}' has no description"
