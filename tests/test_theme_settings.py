"""Перевірки збереження теми застосунку."""

import json

import pytest

from model.storage.json_file import JsonFile
from model.storage.settings import Settings


def test_theme_defaults_to_dark(tmp_path):
    """Використовує темну тему за відсутності файла налаштувань."""
    assert Settings(JsonFile(str(tmp_path / "settings.json"))).theme == "dark"


@pytest.mark.parametrize("stored_theme", ["dark", "light"])
def test_theme_loads_valid_saved_value(tmp_path, stored_theme):
    """Завантажує кожну підтримувану тему з JSON."""
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"theme": stored_theme}), encoding="utf-8")

    assert Settings(JsonFile(str(path))).theme == stored_theme


def test_unknown_saved_theme_falls_back_to_dark(tmp_path):
    """Повертає темну тему, якщо збережене значення невідоме."""
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"theme": "blue"}), encoding="utf-8")

    assert Settings(JsonFile(str(path))).theme == "dark"


def test_setting_theme_persists_value(tmp_path):
    """Зберігає нову тему у JSON."""
    path = tmp_path / "settings.json"
    settings = Settings(JsonFile(str(path)))

    settings.theme = "light"

    assert settings.theme == "light"
    assert json.loads(path.read_text(encoding="utf-8")) == {"theme": "light"}


def test_setting_unknown_theme_raises_value_error(tmp_path):
    """Відхиляє тему, якої немає серед підтримуваних."""
    settings = Settings(JsonFile(str(tmp_path / "settings.json")))

    with pytest.raises(ValueError, match="Невідома тема: blue"):
        settings.theme = "blue"
