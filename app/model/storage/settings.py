"""Збереження обраної теми застосунку."""

from model.storage.json_file import JsonFile

THEMES = ("dark", "light")


class Settings:
    """Налаштування теми застосунку."""

    def __init__(self, json_file: JsonFile):
        """Завантажує тему або встановлює темну за замовчуванням."""
        self._file = json_file
        self._theme = self._load_theme()

    @property
    def theme(self) -> str:
        """Повертає назву активної теми."""
        return self._theme

    @theme.setter
    def theme(self, name: str) -> None:
        """Зберігає тему або піднімає ValueError для невідомого значення."""
        if name not in THEMES:
            raise ValueError(f"Невідома тема: {name}")

        self._theme = name
        self._file.save({"theme": name})

    def _load_theme(self) -> str:
        data = self._file.load(default={})

        if isinstance(data, dict) and data.get("theme") in THEMES:
            return data["theme"]

        return "dark"
