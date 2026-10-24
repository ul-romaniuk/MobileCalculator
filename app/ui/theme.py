from dataclasses import dataclass

from kivy.utils import get_color_from_hex as hex_color


@dataclass(frozen=True)
class ButtonStyle:
    background: tuple
    foreground: tuple


@dataclass(frozen=True)
class Theme:
    name: str
    background: tuple
    surface: tuple  # фон панелей і меню
    text: tuple
    text_muted: tuple
    error: tuple
    button_styles: dict


DARK = Theme(
    name="dark",
    background=hex_color("#14151A"),
    surface=hex_color("#23252C"),
    text=hex_color("#FFFFFF"),
    text_muted=hex_color("#7C8190"),
    error=hex_color("#FF6B6B"),
    button_styles={
        "number": ButtonStyle(hex_color("#23252C"), hex_color("#FFFFFF")),
        "function": ButtonStyle(hex_color("#343741"), hex_color("#FFB86B")),
        "operator": ButtonStyle(hex_color("#F5A623"), hex_color("#14151A")),
        "equals": ButtonStyle(hex_color("#FF7043"), hex_color("#FFFFFF")),
        "secondary": ButtonStyle(hex_color("#1D1F26"), hex_color("#9AA3B5")),
    },
)

LIGHT = Theme(
    name="light",
    background=hex_color("#F2F3F7"),
    surface=hex_color("#FFFFFF"),
    text=hex_color("#14151A"),
    text_muted=hex_color("#6B7080"),
    error=hex_color("#D93025"),
    button_styles={
        "number": ButtonStyle(hex_color("#FFFFFF"), hex_color("#14151A")),
        "function": ButtonStyle(hex_color("#E3E5EC"), hex_color("#D97706")),
        "operator": ButtonStyle(hex_color("#F59E0B"), hex_color("#FFFFFF")),
        "equals": ButtonStyle(hex_color("#FF7043"), hex_color("#FFFFFF")),
        "secondary": ButtonStyle(hex_color("#E9EBF1"), hex_color("#5B6275")),
    },
)

THEMES = {"dark": DARK, "light": LIGHT}


def pressed_variant(color):
    """Колір натиснутої кнопки: світлі кнопки темнішають, темні світлішають."""
    r, g, b, a = color
    brightness = 0.299 * r + 0.587 * g + 0.114 * b

    if brightness > 0.6:
        return (r * 0.88, g * 0.88, b * 0.88, a)

    amount = 0.18
    return (r + (1 - r) * amount, g + (1 - g) * amount, b + (1 - b) * amount, a)