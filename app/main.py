"""Точка входу та складання Kivy-застосунку."""

import os

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.utils import platform

from config import settings
from controllers.calculator_controller import CalculatorController
from models.calculator_model import CalculatorModel
from operations.calculator import Calculator
from storage.history import History
from storage.json_file import JsonFile
from storage.settings import Settings
from ui.about_screen import AboutScreen
from ui.calculator_screen import CalculatorScreen
from ui.history_screen import HistoryScreen
from ui.theme import THEMES


class CalculatorApp(App):
    """Налаштовує Kivy-застосунок і координує екрани."""

    title = settings.app_name

    def build(self):
        """Створює моделі, екрани та менеджер переходів Kivy."""
        data_dir = self.user_data_dir  # на Android це внутрішня папка застосунку

        self.user_settings = Settings(JsonFile(os.path.join(data_dir, "settings.json")))
        self.history = History(JsonFile(os.path.join(data_dir, "history.json")))
        theme = THEMES[self.user_settings.theme]

        calculator = Calculator()
        calculator_model = CalculatorModel(calculator, self.history)
        calculator_controller = CalculatorController(calculator_model)
        self.calculator_screen = CalculatorScreen(
            name="calculator",
            calculator=calculator,
            history=self.history,
            controller=calculator_controller,
            theme=theme,
            open_history_callback=self.show_history,
            select_theme_callback=self.select_theme,
            open_about_callback=self.show_about,
        )
        self.history_screen = HistoryScreen(
            name="history",
            history=self.history,
            theme=theme,
            back_callback=self.show_calculator,
            select_callback=self.use_history_entry,
            clear_callback=self.clear_history,
        )
        self.about_screen = AboutScreen(
            name="about",
            theme=theme,
            back_callback=self.show_calculator,
        )

        self.screens = ScreenManager(transition=SlideTransition(duration=0.2))
        self.screens.add_widget(self.calculator_screen)
        self.screens.add_widget(self.history_screen)
        self.screens.add_widget(self.about_screen)

        Window.clearcolor = theme.background
        Window.bind(on_keyboard=self._on_keyboard)

        return self.screens

    def show_history(self):
        """Відкриває екран історії."""
        self._show("history", "left")

    def show_about(self):
        """Відкриває екран відомостей."""
        self._show("about", "left")

    def show_calculator(self):
        """Повертає користувача до калькулятора."""
        self._show("calculator", "right")

    def _show(self, name, direction):
        """Перемикає поточний екран із заданим напрямком переходу."""
        self.screens.transition.direction = direction
        self.screens.current = name

    def use_history_entry(self, entry):
        """Завантажує вибраний запис у калькулятор."""
        self.calculator_screen.load_expression(entry.recall)
        self.show_calculator()

    def clear_history(self):
        """Очищає історію обчислень."""
        self.history.clear()

    def select_theme(self, name):
        """Застосовує вибрану тему до всіх екранів і зберігає її."""
        if name == self.user_settings.theme:
            return

        self.user_settings.theme = name
        theme = THEMES[name]

        Window.clearcolor = theme.background
        self.calculator_screen.apply_theme(theme)
        self.history_screen.apply_theme(theme)
        self.about_screen.apply_theme(theme)

    def _on_keyboard(self, _window, key, *_args):
        """Обробляє системну клавішу «Назад» або Esc."""
        # 27 це Esc на комп'ютері та кнопка «Назад» на Android
        if key != 27:
            return False

        if self.calculator_screen.close_menu():
            return True

        if self.screens.current != "calculator":
            self.show_calculator()
            return True

        return False


if __name__ == "__main__":
    if platform in ("win", "linux", "macosx"):
        Window.size = (400, 720)  # розмір телефона для тестування на комп'ютері

    CalculatorApp().run()
