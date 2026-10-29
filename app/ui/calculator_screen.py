"""Kivy-подання калькулятора: екран, дисплей та клавіатура."""

from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from controllers.calculator_controller import CalculatorController
from models.calculator_model import CalculatorModel
from operations.calculator import Calculator
from storage.history import History
from ui.widgets import ChoiceMenu, DisplayLabel, ExpandButton, MenuButton, PopupMenu, RoundedButton


KEYPAD = [
    [
        ("AC", "function"),
        ("DEL", "function"),
        ("%", "function"),
        ("÷", "operator"),
    ],
    [
        ("7", "number"),
        ("8", "number"),
        ("9", "number"),
        ("×", "operator"),
    ],
    [
        ("4", "number"),
        ("5", "number"),
        ("6", "number"),
        ("−", "operator"),
    ],
    [
        ("1", "number"),
        ("2", "number"),
        ("3", "number"),
        ("+", "operator"),
    ],
    [
        ("TOGGLE", "function"),
        ("0", "number"),
        (".", "number"),
        ("=", "equals"),
    ],
]

EXTENDED_ROW = [
    ("x²", "function"),
    ("√", "function"),
    ("1/x", "function"),
    ("x^y", "function"),
    ("±", "function"),
]

class CalculatorScreen(Screen):
    """Екран калькулятора з меню, дисплеєм і розширеною клавіатурою."""

    def __init__(
        self,
        calculator: Calculator,
        history: History,
        theme,
        open_history_callback,
        select_theme_callback,
        open_about_callback,
        controller: CalculatorController | None = None,
        **kwargs,
    ):
        """Створює екран із початковими залежностями та діями меню."""
        super().__init__(**kwargs)

        self.controller = controller or CalculatorController(
            CalculatorModel(calculator, history)
        )
        self.theme = theme

        self.open_history_callback = open_history_callback
        self.select_theme_callback = select_theme_callback
        self.open_about_callback = open_about_callback

        self.extended = False
        self._menu = None
        self._styled_buttons = []

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
        )

        self._build_top_bar(layout)
        self._build_display(layout)
        self._build_keypad(layout)

        self.add_widget(layout)
        self.controller.set_change_callback(self._refresh)
        self.apply_theme(theme)

    def _build_top_bar(self, layout):
        bar = BoxLayout(
            size_hint_y=None,
            height=dp(44),
        )

        bar.add_widget(Widget())

        self.menu_button = MenuButton(
            self.theme.button_styles["secondary"],
            size_hint_x=None,
            width=dp(48),
        )
        self.menu_button.bind(
            on_release=lambda *_: self._open_menu()
        )

        self._styled_buttons.append(
            (self.menu_button, "secondary")
        )

        bar.add_widget(self.menu_button)
        layout.add_widget(bar)

    def _build_display(self, layout):
        area = BoxLayout(
            orientation="vertical",
            size_hint_y=0.25,
        )

        self.history_label = DisplayLabel(
            font_size=sp(20),
            size_hint_y=0.3,
        )

        self.display_label = DisplayLabel(
            font_size=sp(64),
            size_hint_y=0.7,
        )

        area.add_widget(self.history_label)
        area.add_widget(self.display_label)

        layout.add_widget(area)

    def _build_keypad(self, layout):
        self.keypad = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=0.75,
        )

        self.extended_row = self._build_row(
            EXTENDED_ROW,
            font_size=22,
        )
        self.extended_row.size_hint_y = None
        self.extended_row.height = dp(54)

        self.main_grid = GridLayout(
            cols=4,
            rows=5,
            spacing=dp(8),
        )

        for row in KEYPAD:
            for label, kind in row:

                if label == "TOGGLE":
                    self.toggle_button = ExpandButton(
                        self.theme.button_styles["function"],
                    )
                    self.toggle_button.bind(
                        on_release=lambda *_: self._set_extended(
                            not self.extended
                        )
                    )

                    self._styled_buttons.append(
                        (self.toggle_button, "function")
                    )

                    self.main_grid.add_widget(
                        self.toggle_button
                    )
                    continue

                button = RoundedButton(
                    self.theme.button_styles[kind],
                    text=label,
                    font_size=sp(
                        24 if label == "DEL" else 28
                    ),
                )

                button.bind(
                    on_release=lambda _button, key=label:
                    self.handle_key(key)
                )

                self._styled_buttons.append(
                    (button, kind)
                )

                self.main_grid.add_widget(button)

        self.keypad.add_widget(self.main_grid)
        layout.add_widget(self.keypad)

    def _build_row(self, row, font_size=24):
        """Створює ряд кнопок додаткових функцій."""
        row_layout = BoxLayout(
            spacing=dp(8),
        )

        for label, kind in row:
            button = RoundedButton(
                self.theme.button_styles[kind],
                text=label,
                font_size=sp(font_size),
            )

            button.bind(
                on_release=lambda _button, key=label:
                self.handle_key(key)
            )

            self._styled_buttons.append(
                (button, kind)
            )

            row_layout.add_widget(button)

        return row_layout

    def _open_menu(self):
        if self._menu is not None:
            return

        self._menu = PopupMenu(
            self.theme,
            items=[
                ("Історія", self.open_history_callback),
                ("Тема", self._open_theme_menu),
                ("Про розробника", self.open_about_callback),
            ],
            dismiss_callback=self.close_menu,
        )

        self.add_widget(self._menu)

    def _open_theme_menu(self):
        """Відкриває меню вибору теми: світла або темна."""
        if self._menu is not None:
            return

        self._menu = ChoiceMenu(
            self.theme,
            options=[("light", "Світла"), ("dark", "Темна")],
            selected=self.theme.name,
            select_callback=self.select_theme_callback,
            dismiss_callback=self.close_menu,
        )

        self.add_widget(self._menu)

    def close_menu(self):
        """Закриває меню та повідомляє, чи було воно відкрите."""
        if self._menu is None:
            return False

        self.remove_widget(self._menu)
        self._menu = None

        return True

    def apply_theme(self, theme):
        """Оновлює кольори віджетів і дисплея."""
        self.theme = theme

        for button, kind in self._styled_buttons:
            button.apply_style(
                theme.button_styles[kind]
            )

        self._update_toggle_button()

        if isinstance(self._menu, ChoiceMenu):
            self._menu.apply_theme(theme, theme.name)

        self.history_label.color = theme.text_muted

        self._refresh()

    def _set_extended(self, enabled):
        """Показує або приховує додаткові функції."""
        self.extended = enabled

        attached = self.extended_row.parent is not None

        if enabled and not attached:
            self.keypad.add_widget(
                self.extended_row,
                index=len(self.keypad.children),
            )

        elif not enabled and attached:
            self.keypad.remove_widget(
                self.extended_row
            )

        self._update_toggle_button()

    def _update_toggle_button(self):
        """Оновлює стиль кнопки розгортання: вона підсвічується, поки функції розкриті."""
        if not hasattr(self, "toggle_button"):
            return

        kind = (
            "operator" if self.extended
            else "function"
        )

        self.toggle_button.apply_style(
            self.theme.button_styles[kind]
        )

    def handle_key(self, key):
        """Передає натискання клавіші контролеру."""
        self.controller.handle_key(key)

    def load_expression(self, expression):
        """Просить контролер завантажити вираз з історії."""
        self.controller.load_expression(expression)

    def _refresh(self):
        if not hasattr(self, "display_label"):
            return

        expression, history_line, error = self.controller.display_state()
        if error:
            text = error
            color = self.theme.error
            size = sp(32)
        else:
            text = expression or "0"
            color = self.theme.text
            size = self._font_size_for(text)

        self.display_label.text = text
        self.display_label.color = color
        self.display_label.font_size = size

        self.history_label.text = history_line

    @staticmethod
    def _font_size_for(text):
        length = len(text)

        if length <= 9:
            return sp(64)
        if length <= 13:
            return sp(48)
        if length <= 18:
            return sp(36)

        return sp(28)
