"""Модель та збереження історії обчислень."""

from dataclasses import dataclass, asdict

from storage.json_file import JsonFile
from config import settings


@dataclass(frozen=True)
class HistoryEntry:
    """Незмінний запис виразу, результату та значення для повторного вводу."""
    expression: str
    result: str
    recall: str

    @classmethod
    def from_dict(cls, data) -> "HistoryEntry | None":
        """Створює запис зі збережених даних. Для пошкоджених даних повертає None."""
        if not isinstance(data, dict):
            return None

        expression, result = data.get("expression"), data.get("result")

        if not isinstance(expression, str) or not isinstance(result, str):
            return None

        recall = data.get("recall")  # у старих файлах цього поля немає
        return cls(expression, result, recall if isinstance(recall, str) else expression)


class History:
    """Останні обчислення з обмеженою кількістю записів."""

    def __init__(self, json_file: JsonFile):
        """Завантажує історію зі сховища."""
        self._file = json_file
        self._entries = self._load()

    @property
    def entries(self) -> list[HistoryEntry]:
        """Повертає копію списку записів від найновішого."""
        return list(self._entries)

    def add(self, expression: str, result: str, recall: str | None = None) -> None:
        """Додає запис і зберігає записи в межах ліміту."""
        self._entries.insert(0, HistoryEntry(expression, result, recall or expression))
        del self._entries[settings.history_limit:]
        self._save()

    def clear(self) -> None:
        """Видаляє всі записи та зберігає порожню історію."""
        self._entries.clear()
        self._save()

    def _load(self) -> list[HistoryEntry]:
        data = self._file.load(default=[])

        if not isinstance(data, list):
            return []

        entries = (HistoryEntry.from_dict(item) for item in data)
        return [entry for entry in entries if entry is not None][: settings.history_limit]

    def _save(self) -> None:
        self._file.save([asdict(entry) for entry in self._entries])
