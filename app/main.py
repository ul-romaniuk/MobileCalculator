"""Точка входу та Kivy-збирання застосунку."""

import os

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.utils import platform

from config import settings
from controller.application_controller import ApplicationController
from controller.calculator_controller import CalculatorController
from model.calculator_model import CalculatorModel
from model.operations.calculator import Calculator
from model.storage.history import History
from model.storage.json_file import JsonFile
from model.storage.settings import Settings as ThemeSettings
from view.about_screen import AboutScreen
from view.calculator_screen import CalculatorScreen
from view.history_screen import HistoryScreen
from view.theme import THEMES


class CalculatorApp(App):
    """Створює залежності Kivy та передає взаємодію контролеру."""

    title = settings.app_name

    def build(self):
        """Створює моделі, подання та контролер застосунку."""
        data_dir = self.user_data_dir
        user_settings = ThemeSettings(JsonFile(os.path.join(data_dir, "settings.json")))
        history = History(JsonFile(os.path.join(data_dir, "history.json")))
        self.user_settings = user_settings
        self.history = history
        theme = THEMES[user_settings.theme]

        calculator = Calculator()
        calculator_model = CalculatorModel(calculator, history)
        calculator_controller = CalculatorController(calculator_model)

        self.calculator_screen = CalculatorScreen(
            theme=theme,
            name="calculator",
        )
        self.history_screen = HistoryScreen(
            theme=theme,
            name="history",
        )
        self.about_screen = AboutScreen(
            theme=theme,
            about_info=settings.about_info,
            name="about",
        )

        self.screens = ScreenManager(transition=SlideTransition(duration=0.2))
        self.screens.add_widget(self.calculator_screen)
        self.screens.add_widget(self.history_screen)
        self.screens.add_widget(self.about_screen)

        self.controller = ApplicationController(
            calculator_controller=calculator_controller,
            history=history,
            user_settings=user_settings,
            screen_manager=self.screens,
            calculator_view=self.calculator_screen,
            history_view=self.history_screen,
            about_view=self.about_screen,
            themes=THEMES,
            on_background_change=self._set_background,
        )

        self._set_background(theme.background)
        Window.bind(on_keyboard=self._on_keyboard)
        return self.screens

    def show_history(self):
        """Передає контролеру дію відкриття історії."""
        self.controller.show_history()

    def show_about(self):
        """Передає контролеру дію відкриття відомостей."""
        self.controller.show_about()

    def show_calculator(self):
        """Передає контролеру дію повернення до калькулятора."""
        self.controller.show_calculator()

    def use_history_entry(self, entry):
        """Передає контролеру вибраний запис історії."""
        self.controller.use_history_entry(entry)

    def clear_history(self):
        """Передає контролеру дію очищення історії."""
        self.controller.clear_history()

    def select_theme(self, name):
        """Передає контролеру вибрану тему."""
        self.controller.select_theme(name)

    def _on_keyboard(self, window, key, *args):
        """Передає системну клавішу контролеру застосунку."""
        return self.controller.handle_back(window, key, *args)

    @staticmethod
    def _set_background(color):
        """Застосовує колір фону вікна Kivy."""
        Window.clearcolor = color


if __name__ == "__main__":
    if platform in ("win", "linux", "macosx"):
        Window.size = (400, 720)

    CalculatorApp().run()
