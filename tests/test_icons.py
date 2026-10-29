"""Перевірки створення згладжених текстур значків."""

from view.icons import disc, even_size, expand_icon, ring


def test_even_size_returns_positive_even_pixels():
    """Округлює розмір до парного значення не меншого за два."""
    assert even_size(1) == 2
    assert even_size(5) == 4
    assert even_size(6) == 6


def test_icon_factories_return_requested_texture_sizes():
    """Створює текстури кільця, диска й значка розширення заданого розміру."""
    for texture in (ring(16), disc(16), expand_icon(16)):
        assert texture.size == (16, 16)
