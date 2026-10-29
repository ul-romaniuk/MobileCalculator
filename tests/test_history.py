"""Перевірки моделі історії та сумісності збережених записів."""

import json

from model.storage.history import History, HistoryEntry
from model.storage.json_file import JsonFile
from config import settings


def test_history_persists_entries_and_recall_value(tmp_path):
    """Записує обчислення у JSON та відновлює його після створення моделі."""
    path = tmp_path / "history.json"
    history = History(JsonFile(str(path)))
    history.add("2+3", "5", recall="5")

    restored = History(JsonFile(str(path)))

    assert [(entry.expression, entry.result, entry.recall) for entry in restored.entries] == [
        ("2+3", "5", "5")
    ]


def test_history_defaults_recall_to_expression(tmp_path):
    """Для старих записів без поля recall використовує сам вираз."""
    path = tmp_path / "history.json"
    path.write_text(json.dumps([{"expression": "1+1", "result": "2"}]), encoding="utf-8")

    entry = History(JsonFile(str(path))).entries[0]

    assert entry.recall == "1+1"


def test_history_rejects_malformed_records(tmp_path):
    """Пропускає записи з відсутніми або неправильними обов'язковими полями."""
    path = tmp_path / "history.json"
    path.write_text(
        json.dumps([
            None,
            {"expression": 1, "result": "2"},
            {"expression": "1+1", "result": []},
            {"expression": "3+4", "result": "7"},
        ]),
        encoding="utf-8",
    )

    entries = History(JsonFile(str(path))).entries

    assert [(entry.expression, entry.result) for entry in entries] == [("3+4", "7")]


def test_history_is_limited_to_configured_capacity(tmp_path):
    """Зберігає лише задану кількість найновіших результатів."""
    path = tmp_path / "history.json"
    history = History(JsonFile(str(path)))

    for number in range(settings.history_limit + 3):
        history.add(str(number), str(number))

    assert len(history.entries) == settings.history_limit
    assert history.entries[0].expression == str(settings.history_limit + 2)
    assert history.entries[-1].expression == "3"


def test_history_clear_persists_empty_list(tmp_path):
    """Очищає записи в пам'яті та збережений JSON."""
    path = tmp_path / "history.json"
    history = History(JsonFile(str(path)))
    history.add("1+1", "2")

    history.clear()

    assert history.entries == []
    assert json.loads(path.read_text(encoding="utf-8")) == []


def test_history_entry_from_dict_requires_mapping():
    """Не створює запис з несловникового значення."""
    assert HistoryEntry.from_dict(["1+1", "2"]) is None


def test_history_uses_expression_when_recall_has_wrong_type(tmp_path):
    """Замінює некоректне поле recall значенням виразу."""
    path = tmp_path / "history.json"
    path.write_text(
        json.dumps([{"expression": "3+4", "result": "7", "recall": 7}]),
        encoding="utf-8",
    )

    assert History(JsonFile(str(path))).entries[0].recall == "3+4"


def test_history_rejects_non_list_document(tmp_path):
    """Повертає порожню історію, якщо кореневе JSON-значення не є списком."""
    path = tmp_path / "history.json"
    path.write_text(json.dumps({"expression": "1+1"}), encoding="utf-8")

    assert History(JsonFile(str(path))).entries == []


def test_history_load_truncates_old_records(tmp_path):
    """Під час завантаження застосовує ліміт до вже збережених записів."""
    path = tmp_path / "history.json"
    records = [
        {"expression": str(index), "result": str(index)}
        for index in range(settings.history_limit + 4)
    ]
    path.write_text(json.dumps(records), encoding="utf-8")

    entries = History(JsonFile(str(path))).entries

    assert len(entries) == settings.history_limit
    assert entries[0].expression == "0"
