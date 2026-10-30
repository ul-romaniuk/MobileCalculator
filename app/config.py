
"""Налаштування застосунку та відомості для екрана «Про розробника»."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Settings:
    """Налаштування застосунку."""

    app_name: str = "Калькулятор"
    app_version: str = "1.2.4"
    developer: str = "Романюк Уляна"
    group: str = "IT-41з"
    university: str = (
        "Львівський національний університет ветеринарної "
        "медицини та біотехнологій імені Степана Ґжицького"
    )
    purpose: str = (
        "Курсовий проєкт з дисципліни "
        "«Програмування мобільних платформ»"
    )

    history_limit: int = 10
    result_precision: Decimal = Decimal("1e-10")
    max_display_length: int = 16
    scientific_threshold_high: int = 16
    scientific_threshold_low: int = -7

    @property
    def about_info(self) -> list[tuple[str, str]]:
        """Формує дані для екрана «Про розробника»."""
        return [
            ("Розробник", self.developer),
            ("Група", self.group),
            ("Навчальний заклад", self.university),
            ("Призначення", self.purpose),
            ("Версія", self.app_version),
        ]


settings = Settings()
