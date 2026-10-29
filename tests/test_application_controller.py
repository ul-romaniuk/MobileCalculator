"""Перевірки маршрутизації та оновлення подань контролером застосунку."""

from types import SimpleNamespace

from controller.application_controller import ApplicationController


class FakeCalculatorController:
    """Контролер калькулятора для перевірки зв'язування подань."""

    def __init__(self):
        self.change_callback = None
        self.loaded_expression = None

    def handle_key(self, key):
        self.last_key = key

    def load_expression(self, expression):
        self.loaded_expression = expression

    def set_change_callback(self, callback):
        self.change_callback = callback

    def display_state(self):
        return "12", "", None


class FakeHistory:
    """Історія в пам'яті для перевірки дій контролера."""

    def __init__(self):
        self.entries = [SimpleNamespace(recall="2+3")]
        self.was_cleared = False

    def clear(self):
        self.was_cleared = True
        self.entries.clear()


class FakeView:
    """Подання, що записує передані контролером дані й дії."""

    def __init__(self):
        self.display_state = None
        self.entries = None
        self.actions = None
        self.theme = None
        self.menu_open = False

    def set_actions(self, **actions):
        self.actions = actions

    def set_back_action(self, action):
        self.back_action = action

    def set_display_state(self, *state):
        self.display_state = state

    def set_entries(self, entries):
        self.entries = entries

    def apply_theme(self, theme):
        self.theme = theme

    def close_menu(self):
        was_open = self.menu_open
        self.menu_open = False
        return was_open


class FakeScreenManager:
    """Мінімальний екранний менеджер для тесту навігації."""

    def __init__(self):
        self.current = "calculator"
        self.transition = SimpleNamespace(direction=None)


def make_controller():
    """Збирає контролер застосунку з тестовими залежностями."""
    calculator = FakeCalculatorController()
    history = FakeHistory()
    user_settings = SimpleNamespace(theme="dark")
    screens = FakeScreenManager()
    calculator_view = FakeView()
    history_view = FakeView()
    about_view = FakeView()
    themes = {
        "light": SimpleNamespace(name="light", background="white"),
        "dark": SimpleNamespace(name="dark", background="black"),
    }
    background = []

    controller = ApplicationController(
        calculator_controller=calculator,
        history=history,
        user_settings=user_settings,
        screen_manager=screens,
        calculator_view=calculator_view,
        history_view=history_view,
        about_view=about_view,
        themes=themes,
        on_background_change=background.append,
    )
    return controller, calculator, history, screens, calculator_view, history_view, about_view, user_settings, background


def test_controller_connects_actions_and_initial_display():
    """Підключає події подань і передає їм стан дисплея."""
    controller, calculator, _, _, calculator_view, history_view, about_view, _, _ = make_controller()

    assert calculator_view.display_state == ("12", "", None)
    assert calculator_view.actions["on_key"] == calculator.handle_key
    assert history_view.actions["on_clear"] == controller.clear_history
    assert about_view.back_action == controller.show_calculator


def test_history_and_navigation_actions():
    """Оновлює історію, завантажує вибраний вираз і переходить між екранами."""
    controller, calculator, history, screens, _, history_view, _, _, _ = make_controller()

    controller.show_history()
    assert (screens.current, screens.transition.direction) == ("history", "left")

    controller.refresh_history()
    assert history_view.entries == history.entries

    controller.use_history_entry(history.entries[0])
    assert calculator.loaded_expression == "2+3"
    assert (screens.current, screens.transition.direction) == ("calculator", "right")


def test_clear_history_updates_history_view():
    """Очищає модель історії й оновлює відображений список."""
    controller, _, history, _, _, history_view, _, _, _ = make_controller()

    controller.clear_history()

    assert history.was_cleared
    assert history_view.entries == []


def test_theme_and_back_actions():
    """Змінює тему подань і обробляє системну кнопку повернення."""
    controller, _, _, screens, calculator_view, history_view, about_view, settings, backgrounds = make_controller()

    controller.select_theme("light")
    assert settings.theme == "light"
    assert calculator_view.theme.name == history_view.theme.name == about_view.theme.name == "light"
    assert backgrounds == ["white"]

    controller.select_theme("light")
    assert backgrounds == ["white"]

    controller.show_about()
    assert (screens.current, screens.transition.direction) == ("about", "left")

    screens.current = "history"
    assert controller.handle_back(None, 27)
    assert screens.current == "calculator"
    assert controller.handle_back(None, 13) is False


def test_back_action_closes_menu_or_stays_on_calculator():
    """Закриває меню, а Esc на калькуляторі не перемикає екран."""
    controller, _, _, screens, calculator_view, _, _, _, _ = make_controller()
    calculator_view.menu_open = True

    assert controller.handle_back(None, 27)
    assert calculator_view.menu_open is False
    assert screens.current == "calculator"
    assert controller.handle_back(None, 27) is False
