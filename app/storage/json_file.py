"""Безпечне читання й атомарний запис JSON-файлів."""

import json
import os


class JsonFile:
    """Читає та записує один JSON-файл. Помилки файлу не ламають застосунок."""

    def __init__(self, path: str):
        """Створює об'єкт для роботи з файлом за вказаним шляхом."""
        self.path = path

    def load(self, default=None):
        """Повертає дані з файлу або default, якщо файлу немає чи він пошкоджений."""
        try:
            with open(self.path, encoding="utf-8") as file:
                return json.load(file)
        except (OSError, ValueError):
            return default

    def save(self, data) -> bool:
        """Записує дані через тимчасовий файл, щоб не залишити половину запису."""
        temp_path = self.path + ".tmp"

        try:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)

            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

            os.replace(temp_path, self.path)
            return True
        except OSError:
            return False
