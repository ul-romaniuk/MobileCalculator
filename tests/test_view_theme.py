"""Перевірки стилів і кольорів Kivy-подання."""

import pytest

from view.theme import THEMES, pressed_variant


@pytest.mark.parametrize("name", ["dark", "light"])
def test_theme_has_styles_for_all_button_roles(name):
    """Кожна тема містить кольори для всіх типів кнопок."""
    assert set(THEMES[name].button_styles) == {
        "number", "function", "operator", "equals", "secondary"
    }


def test_pressed_variant_darkens_light_color():
    """Затемнює світлий колір кнопки в натиснутому стані."""
    color = (0.9, 0.9, 0.9, 1.0)

    assert pressed_variant(color) == (0.9 * 0.88, 0.9 * 0.88, 0.9 * 0.88, 1.0)


def test_pressed_variant_lightens_dark_color():
    """Освітлює темний колір кнопки в натиснутому стані."""
    color = (0.0, 0.0, 0.0, 1.0)

    assert pressed_variant(color) == (0.18, 0.18, 0.18, 1.0)
