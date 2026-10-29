"""Перевірки складання Kivy-застосунку та його публічних дій."""

from kivy.core.window import Window

from main import CalculatorApp


class CalculatorAppForTest(CalculatorApp):
    """Застосунок, що зберігає тестові дані у тимчасовій папці."""

    def __init__(self, data_dir):
        self._test_data_dir = str(data_dir)
        super().__init__()

    @property
    def user_data_dir(self):
        return self._test_data_dir


def test_app_build_connects_screens_and_public_actions(tmp_path):
    """Збирає екрани та зберігає роботу публічних методів застосунку."""
    app = CalculatorAppForTest(tmp_path)
    screen_manager = app.build()
    try:
        assert {screen.name for screen in screen_manager.screens} == {
            "calculator", "history", "about"
        }

        app.show_history()
        assert screen_manager.current == "history"
        app.show_about()
        assert screen_manager.current == "about"
        app.show_calculator()
        assert screen_manager.current == "calculator"

        app.history.add("2+3", "5")
        app.controller.refresh_history()
        assert len(app.history_screen.items.children) == 1
        app.use_history_entry(app.history.entries[0])
        assert app.controller.calculator_controller.display_state()[0] == "2+3"

        app.select_theme("light")
        assert app.user_settings.theme == "light"
        app.clear_history()
        assert app.history.entries == []
        assert app.history_screen.items.children[0].text == "Історія порожня"
    finally:
        Window.unbind(on_keyboard=app._on_keyboard)
