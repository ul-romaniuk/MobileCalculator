"""Перевірки JSON-сховища та його поведінки при помилках."""

import json

from model.storage.json_file import JsonFile


def test_load_missing_file_returns_default(tmp_path):
    """Повертає передане значення за замовчуванням для відсутнього файла."""
    assert JsonFile(str(tmp_path / "missing.json")).load(default={"x": 1}) == {"x": 1}


def test_load_invalid_json_returns_default(tmp_path):
    """Повертає default, якщо файл містить пошкоджений JSON."""
    path = tmp_path / "broken.json"
    path.write_text("{broken", encoding="utf-8")

    assert JsonFile(str(path)).load(default=[]) == []


def test_save_creates_parent_and_writes_utf8_json(tmp_path):
    """Створює вкладені папки й записує JSON без екранування українських літер."""
    path = tmp_path / "nested" / "data.json"
    storage = JsonFile(str(path))

    assert storage.save({"назва": "Калькулятор"})
    assert json.loads(path.read_text(encoding="utf-8")) == {"назва": "Калькулятор"}
    assert not path.with_suffix(".json.tmp").exists()


def test_save_returns_false_when_file_cannot_be_written(tmp_path, monkeypatch):
    """Повертає False, якщо атомарний запис завершується помилкою ОС."""
    storage = JsonFile(str(tmp_path / "data.json"))

    def fail_replace(_source, _destination):
        raise OSError("read-only filesystem")

    monkeypatch.setattr("model.storage.json_file.os.replace", fail_replace)

    assert storage.save({"value": 1}) is False
