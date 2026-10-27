from dataclasses import dataclass, asdict

from storage.json_file import JsonFile


@dataclass(frozen=True)
class HistoryEntry:
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
    """Останні обчислення. Нові записи додаються на початок, зберігається не більше 10."""

    MAX_ENTRIES = 10

    def __init__(self, json_file: JsonFile):
        self._file = json_file
        self._entries = self._load()

    @property
    def entries(self) -> list[HistoryEntry]:
        return list(self._entries)

    def add(self, expression: str, result: str, recall: str | None = None) -> None:
        self._entries.insert(0, HistoryEntry(expression, result, recall or expression))
        del self._entries[self.MAX_ENTRIES:]
        self._save()

    def clear(self) -> None:
        self._entries.clear()
        self._save()

    def _load(self) -> list[HistoryEntry]:
        data = self._file.load(default=[])

        if not isinstance(data, list):
            return []

        entries = (HistoryEntry.from_dict(item) for item in data)
        return [entry for entry in entries if entry is not None][: self.MAX_ENTRIES]

    def _save(self) -> None:
        self._file.save([asdict(entry) for entry in self._entries])