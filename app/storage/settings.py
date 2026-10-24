from storage.json_file import JsonFile

THEMES = ("dark", "light")


class Settings:
    """Налаштування застосунку (поки що лише тема)."""

    def __init__(self, json_file: JsonFile):
        self._file = json_file
        self._theme = self._load_theme()

    @property
    def theme(self) -> str:
        return self._theme

    @theme.setter
    def theme(self, name: str) -> None:
        if name not in THEMES:
            raise ValueError(f"Невідома тема: {name}")

        self._theme = name
        self._file.save({"theme": name})

    def _load_theme(self) -> str:
        data = self._file.load(default={})

        if isinstance(data, dict) and data.get("theme") in THEMES:
            return data["theme"]

        return "dark"