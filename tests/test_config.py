"""Перевірки конфігурації застосунку та її змінних середовища."""

from config import Settings


ENV_FIELDS = (
    "APP_NAME",
    "APP_VERSION",
    "APP_DESCRIPTION",
    "DEVELOPER",
    "GROUP",
    "UNIVERSITY",
    "PURPOSE",
    "YEAR",
)


def test_settings_use_defaults_without_environment(monkeypatch):
    """Завантажує типові значення без .env і змінних середовища."""
    for field in ENV_FIELDS:
        monkeypatch.delenv(field, raising=False)
    settings = Settings(_env_file=None)

    assert settings.app_name == "Назва застосунку"
    assert settings.app_version == "Версія"
    assert settings.developer == "Розробник"
    assert settings.group == "Група"
    assert settings.year == 0
    assert settings.history_limit == 10
    assert settings.about_info[0] == ("Застосунок", "Назва застосунку")


def test_settings_load_values_from_env_file(tmp_path, monkeypatch):
    """Зчитує типізовані значення й текст українською з .env-файла."""
    for field in ENV_FIELDS:
        monkeypatch.delenv(field, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "APP_NAME=Мій калькулятор\nAPP_VERSION=2.0\nYEAR=2025\nGROUP=КН-1\n",
        encoding="utf-8",
    )

    settings = Settings(_env_file=env_file)

    assert settings.app_name == "Мій калькулятор"
    assert settings.app_version == "2.0"
    assert settings.year == 2025
    assert settings.group == "КН-1"


def test_about_info_excludes_internal_calculation_settings():
    """Показує лише відомості застосунку, а не технічні параметри."""
    settings = Settings(_env_file=None, app_name="Тест", year=2024)

    assert settings.about_info == [
        ("Застосунок", "Тест"),
        ("Опис", "Опис застосунку"),
        ("Версія", "Версія"),
        ("Розробник", "Розробник"),
        ("Група", "Група"),
        ("Навчальний заклад", "Навчальний заклад"),
        ("Призначення", "Призначення"),
        ("Рік розробки", "2024"),
    ]


def test_settings_loads_dotenv_from_working_directory(tmp_path, monkeypatch):
    """Завантажує .env з кореня проєкту, звідки запускається застосунок."""
    for field in ENV_FIELDS:
        monkeypatch.delenv(field, raising=False)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("APP_NAME=Курсовий калькулятор\nYEAR=2026\n", encoding="utf-8")

    settings = Settings()

    assert settings.app_name == "Курсовий калькулятор"
    assert settings.year == 2026
