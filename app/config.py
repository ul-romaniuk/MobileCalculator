"""Налаштування застосунку та відомості для екрана «Про розробника»."""

from decimal import Decimal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Налаштування застосунку із змінних середовища або заглушок."""

    app_name: str = Field(default="Назва застосунку", title="Застосунок", description="Назва калькулятора")
    app_version: str = Field(default="Версія", title="Версія", description="Версія застосунку")
    app_description: str = Field(default="Опис застосунку", title="Опис", description="Короткий опис застосунку")
    developer: str = Field(default="Розробник", title="Розробник", description="Ім'я розробника")
    group: str = Field(default="Група", title="Група", description="Навчальна група")
    university: str = Field(default="Навчальний заклад", title="Навчальний заклад", description="Назва навчального закладу")
    purpose: str = Field(default="Призначення", title="Призначення", description="Навчальне або практичне призначення")
    year: int = Field(default=0, title="Рік розробки", description="Рік розробки")

    history_limit: int = Field(default=10, exclude=True, description="Максимальна кількість записів історії")
    result_precision: Decimal = Field(default=Decimal("1e-10"), exclude=True, description="Точність округлення результату")
    max_display_length: int = Field(default=16, exclude=True, description="Максимальна довжина звичайного запису")
    scientific_threshold_high: int = Field(default=16, exclude=True, description="Верхній поріг наукового запису")
    scientific_threshold_low: int = Field(default=-7, exclude=True, description="Нижній поріг наукового запису")

    @property
    def about_info(self) -> list[tuple[str, str]]:
        """Формує підписи й значення полів для екрана відомостей."""
        return [
            ("Застосунок", self.app_name),
            ("Опис", self.app_description),
            ("Версія", self.app_version),
            ("Розробник", self.developer),
            ("Група", self.group),
            ("Навчальний заклад", self.university),
            ("Призначення", self.purpose),
            ("Рік розробки", str(self.year)),
        ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
