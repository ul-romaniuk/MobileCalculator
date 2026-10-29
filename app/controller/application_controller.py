"""Координує навігацію та взаємодію моделей із Kivy-поданнями."""

from controller.calculator_controller import CalculatorController
from model.storage.history import History
from model.storage.settings import Settings as ThemeSettings


class ApplicationController:
    """Обробляє навігацію, історію й тему застосунку."""

    def __init__(
        self,
        calculator_controller: CalculatorController,
        history: History,
        user_settings: ThemeSettings,
        screen_manager,
        calculator_view,
        history_view,
        about_view,
        themes,
        on_background_change,
    ):
        """З'єднує контролери, моделі та екрани застосунку."""
        self.calculator_controller = calculator_controller
        self.history = history
        self.user_settings = user_settings
        self.screen_manager = screen_manager
        self.calculator_view = calculator_view
        self.history_view = history_view
        self.about_view = about_view
        self.themes = themes
        self.on_background_change = on_background_change

        calculator_view.set_actions(
            on_key=calculator_controller.handle_key,
            on_load_expression=calculator_controller.load_expression,
            on_open_history=self.show_history,
            on_select_theme=self.select_theme,
            on_open_about=self.show_about,
        )
        calculator_controller.set_change_callback(self._update_calculator_view)
        history_view.set_actions(
            on_back=self.show_calculator,
            on_select=self.use_history_entry,
            on_clear=self.clear_history,
            on_enter=self.refresh_history,
        )
        about_view.set_back_action(self.show_calculator)
        self._update_calculator_view()

    def show_history(self):
        """Відкриває екран історії."""
        self._show("history", "left")

    def refresh_history(self):
        """Передає актуальні записи історії до подання."""
        self.history_view.set_entries(self.history.entries)

    def show_about(self):
        """Відкриває екран відомостей про застосунок."""
        self._show("about", "left")

    def show_calculator(self):
        """Повертає користувача до екрана калькулятора."""
        self._show("calculator", "right")

    def use_history_entry(self, entry):
        """Завантажує вибраний запис у калькулятор."""
        self.calculator_controller.load_expression(entry.recall)
        self.show_calculator()

    def clear_history(self):
        """Очищає історію та оновлює її подання."""
        self.history.clear()
        self.refresh_history()

    def select_theme(self, name):
        """Зберігає вибрану тему й оновлює всі екрани."""
        if name == self.user_settings.theme:
            return

        self.user_settings.theme = name
        theme = self.themes[name]
        self.on_background_change(theme.background)
        self.calculator_view.apply_theme(theme)
        self.history_view.apply_theme(theme)
        self.about_view.apply_theme(theme)

    def handle_back(self, _window, key, *_args):
        """Обробляє Esc або системну кнопку повернення Android."""
        if key != 27:
            return False

        if self.calculator_view.close_menu():
            return True

        if self.screen_manager.current != "calculator":
            self.show_calculator()
            return True

        return False

    def _show(self, name, direction):
        """Перемикає активний екран у вказаному напрямку."""
        self.screen_manager.transition.direction = direction
        self.screen_manager.current = name

    def _update_calculator_view(self):
        """Передає стан моделі дисплею калькулятора."""
        self.calculator_view.set_display_state(
            *self.calculator_controller.display_state()
        )
