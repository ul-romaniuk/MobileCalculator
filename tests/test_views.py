"""Перевірки відображення стану та передачі подій Kivy-поданнями."""

from types import SimpleNamespace

from view.about_screen import AboutScreen
from view.calculator_screen import CalculatorScreen
from view.history_screen import HistoryScreen
from view.theme import THEMES


def test_calculator_view_forwards_keys_and_load_requests():
    """Передає клавіші й запит завантаження виразу контролеру."""
    screen = CalculatorScreen(theme=THEMES["dark"])
    actions = []
    screen.set_actions(
        on_key=lambda key: actions.append(("key", key)),
        on_load_expression=lambda expression: actions.append(("load", expression)),
        on_open_history=lambda: None,
        on_select_theme=lambda name: None,
        on_open_about=lambda: None,
    )

    screen.handle_key("7")
    screen.load_expression("2+3")

    assert actions == [("key", "7"), ("load", "2+3")]


def test_calculator_view_renders_normal_and_error_states():
    """Показує вираз, історичний рядок і текст помилки."""
    screen = CalculatorScreen(theme=THEMES["dark"])

    screen.set_display_state("25", "5² =", None)
    assert screen.display_label.text == "25"
    assert screen.history_label.text == "5² ="
    assert screen.display_label.color == THEMES["dark"].text

    screen.set_display_state("", "", "Ділення на нуль")
    assert screen.display_label.text == "Ділення на нуль"
    assert screen.display_label.color == THEMES["dark"].error


def test_calculator_view_menu_and_extended_keypad_actions():
    """Перемикає розширену клавіатуру та передає вибір пункту меню."""
    screen = CalculatorScreen(theme=THEMES["dark"])
    history_opened = []
    screen.set_actions(
        on_key=lambda _key: None,
        on_load_expression=lambda _expression: None,
        on_open_history=lambda: history_opened.append(True),
        on_select_theme=lambda _name: None,
        on_open_about=lambda: None,
    )

    screen.toggle_button.dispatch("on_release")
    assert screen.extended
    assert screen.extended_row.parent is screen.keypad

    screen.toggle_button.dispatch("on_release")
    assert not screen.extended
    assert screen.extended_row.parent is None

    screen._open_menu()
    history_item = next(item for item in screen._menu.panel.children if item.text == "Історія")
    history_item.dispatch("on_release")

    assert history_opened == [True]
    assert screen.close_menu() is False


def test_calculator_view_theme_menu_forwards_selection():
    """Передає вибір теми з меню контролеру."""
    screen = CalculatorScreen(theme=THEMES["dark"])
    selected = []
    screen.set_actions(
        on_key=lambda _key: None,
        on_load_expression=lambda _expression: None,
        on_open_history=lambda: None,
        on_select_theme=selected.append,
        on_open_about=lambda: None,
    )

    screen._open_theme_menu()
    screen._menu._rows["light"].dispatch("on_release")

    assert selected == ["light"]
    assert screen.close_menu()


def test_history_view_renders_entries_and_forwards_actions():
    """Показує записи й передає повернення, очищення та вибір контролеру."""
    screen = HistoryScreen(theme=THEMES["dark"])
    entry = SimpleNamespace(expression="2+3", result="5", recall="5")
    calls = []
    screen.set_actions(
        on_back=lambda: calls.append("back"),
        on_select=lambda selected: calls.append(("select", selected)),
        on_clear=lambda: calls.append("clear"),
        on_enter=lambda: calls.append("enter"),
    )

    screen.set_entries([entry])
    assert len(screen.items.children) == 1
    screen.items.children[0].dispatch("on_release")
    screen.back_button.dispatch("on_release")
    screen.clear_button.dispatch("on_release")
    screen.on_pre_enter()

    assert calls == [("select", entry), "back", "clear", "enter"]


def test_history_view_empty_state_and_theme():
    """Показує порожній стан і перемальовує його після зміни теми."""
    screen = HistoryScreen(theme=THEMES["dark"])
    screen.set_entries([])

    assert screen.items.children[0].text == "Історія порожня"

    screen.apply_theme(THEMES["light"])
    assert screen.title_label.color == THEMES["light"].text
    assert screen.items.children[0].text == "Історія порожня"


def test_about_view_renders_given_information_and_returns():
    """Відображає передані відомості й передає дію повернення."""
    info = [("Застосунок", "Калькулятор"), ("Версія", "1.0.0")]
    screen = AboutScreen(theme=THEMES["dark"], about_info=info)
    returned = []
    screen.set_back_action(lambda: returned.append(True))

    assert [label.text for label in screen.captions] == ["Застосунок", "Версія"]
    assert [label.text for label in screen.values] == ["Калькулятор", "1.0.0"]

    screen.back_button.dispatch("on_release")
    screen.apply_theme(THEMES["light"])

    assert returned == [True]
    assert screen.title_label.color == THEMES["light"].text
