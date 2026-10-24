
from decimal import Decimal, InvalidOperation

from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from operations.calculator import Calculator
from operations.errors import CalculatorError
from storage.history import History
from ui.widgets import DisplayLabel, MenuButton, PopupMenu, RoundedButton


DIGITS = "0123456789"
OPERATORS = "+−×÷^"
KEY_ALIASES = {"x^y": "^"}

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
        ("TOGGLE", "secondary"),
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

UNARY_HISTORY_TEMPLATES = {
    "x²": "({})²",
    "√": "√({})",
    "1/x": "1/({})",
}


class CalculatorScreen(Screen):
    """Екран калькулятора з меню, дисплеєм і розширеною клавіатурою."""

    def __init__(
        self,
        calculator: Calculator,
        history: History,
        theme,
        open_history_callback,
        toggle_theme_callback,
        open_about_callback,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.calculator = calculator
        self.history = history
        self.theme = theme

        self.open_history_callback = open_history_callback
        self.toggle_theme_callback = toggle_theme_callback
        self.open_about_callback = open_about_callback

        self.expression = ""
        self.history_line = ""
        self.error = None
        self.just_evaluated = False
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
        self.apply_theme(theme)

    # ---------- Верхня панель ----------

    def _build_top_bar(self, layout):
        bar = BoxLayout(
            size_hint_y=None,
            height=dp(44),
        )

        # Порожній простір ліворуч.
        # Кнопка розгортання розташована в клавіатурі.
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

    # ---------- Дисплей ----------

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

    # ---------- Клавіатура ----------

    def _build_keypad(self, layout):
        self.keypad = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=0.75,
        )

        # Додатковий ряд прихований до натискання стрілки.
        self.extended_row = self._build_row(
            EXTENDED_ROW,
            font_size=22,
        )
        self.extended_row.size_hint_y = None
        self.extended_row.height = dp(54)

        # Основна клавіатура: 5 рядків і 4 стовпці.
        self.main_grid = GridLayout(
            cols=4,
            rows=5,
            spacing=dp(8),
        )

        for row in KEYPAD:
            for label, kind in row:

                if label == "TOGGLE":
                    self.toggle_button = RoundedButton(
                        self.theme.button_styles["secondary"],
                        text="▼",
                        font_size=sp(20),
                    )
                    self.toggle_button.bind(
                        on_release=lambda *_: self._set_extended(
                            not self.extended
                        )
                    )

                    self._styled_buttons.append(
                        (self.toggle_button, "secondary")
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

        # Основна клавіатура залишається на місці.
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

    # ---------- Меню ----------

    def _open_menu(self):
        if self._menu is not None:
            return

        self._menu = PopupMenu(
            self.theme,
            items=[
                ("Історія", self.open_history_callback),
                ("Тема", self.toggle_theme_callback),
                ("Про розробника", self.open_about_callback),
            ],
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

    # ---------- Тема та додаткові функції ----------

    def apply_theme(self, theme):
        self.theme = theme

        for button, kind in self._styled_buttons:
            button.apply_style(
                theme.button_styles[kind]
            )

        self._update_toggle_button()

        self.history_label.color = theme.text_muted

        self._refresh()

    def _set_extended(self, enabled):
        """Показує або приховує додаткові функції."""
        self.extended = enabled

        attached = self.extended_row.parent is not None

        if enabled and not attached:
            # У вертикальному BoxLayout останній доданий
            # елемент розташовується над попередніми.
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
        """Оновлює стрілку та стиль кнопки розгортання."""
        if not hasattr(self, "toggle_button"):
            return

        self.toggle_button.text = (
            "▲" if self.extended else "▼"
        )

        kind = (
            "operator" if self.extended
            else "secondary"
        )

        self.toggle_button.apply_style(
            self.theme.button_styles[kind]
        )

    # ---------- Обробка натискань ----------

    def handle_key(self, key):
        key = KEY_ALIASES.get(key, key)

        if key in DIGITS:
            self._input_digit(key)

        elif key == ".":
            self._input_dot()

        elif key == "%":
            self._apply_percent()

        elif key in OPERATORS:
            self._input_operator(key)

        elif key in self.calculator.unary_operations:
            self._apply_unary(key)

        elif key == "=":
            self._evaluate()

        elif key in ("DEL", "⌫"):
            self._delete_last()

        elif key in ("AC", "C"):
            self._clear()

        self._refresh()

    def load_expression(self, expression):
        """Завантажує вираз з історії."""
        self._clear()
        self.expression = expression
        self._refresh()

    def _input_digit(self, digit):
        if self.just_evaluated or self.error:
            self._clear()

        current = self._current_number()

        if current == "0":
            self.expression = self.expression[:-1] + digit
        else:
            self.expression += digit

    def _input_dot(self):
        if self.just_evaluated or self.error:
            self._clear()

        current = self._current_number()

        if "." in current:
            return

        self.expression += "." if current else "0."

    def _input_operator(self, operator):
        if self.error:
            return

        self.just_evaluated = False
        self.history_line = ""

        if not self.expression:
            if operator == "−":
                self.expression = operator
            return

        last = self.expression[-1]

        if last in OPERATORS:
            if operator == "−" and last in "×÷^":
                self.expression += operator
                return

            base = self.expression.rstrip(OPERATORS)

            if base:
                self.expression = base + operator
        else:
            self.expression += operator

    def _apply_unary(self, symbol):
        """Застосовує унарну операцію до останнього числа."""
        if self.error or not self._current_number():
            return

        start = self._operand_start()
        operand = self.expression[start:]

        try:
            value = Decimal(
                operand.replace("−", "-")
            )
        except InvalidOperation:
            return

        try:
            result = self.calculator.apply_unary(
                symbol,
                value,
            )
        except CalculatorError as error:
            self.error = str(error)
            return

        text = self._format(result)

        template = UNARY_HISTORY_TEMPLATES.get(symbol)

        if template:
            self.history.add(
                template.format(operand),
                text,
                recall=text,
            )

        self.expression = self.expression[:start] + text
        self.history_line = ""
        self.just_evaluated = False

    def _apply_percent(self):
        """Перетворює останнє число на відсоткове значення."""
        if self.error or not self._current_number():
            return

        start = self._operand_start()
        operand = self.expression[start:]

        try:
            value = Decimal(
                operand.replace("−", "-")
            )
            result = value / Decimal("100")
        except (InvalidOperation, ZeroDivisionError):
            return

        self.expression = (
            self.expression[:start] + self._format(result)
        )
        self.history_line = ""
        self.just_evaluated = False

    def _delete_last(self):
        if self.error:
            self._clear()
            return

        self.just_evaluated = False
        self.history_line = ""
        self.expression = self.expression[:-1]

    def _clear(self):
        self.expression = ""
        self.history_line = ""
        self.error = None
        self.just_evaluated = False

    def _evaluate(self):
        if (
            not self.expression
            or self.error
            or self.just_evaluated
        ):
            return

        try:
            result = self.calculator.calculate(
                self.expression
            )
        except CalculatorError as error:
            self.error = str(error)
            return

        text = self._format(result)

        if text != self.expression:
            self.history.add(
                self.expression,
                text,
            )

        self.history_line = f"{self.expression} ="
        self.expression = text
        self.just_evaluated = True

    # ---------- Допоміжні методи ----------

    def _format(self, value):
        return self.calculator.format_result(
            value
        ).replace("-", "−")

    def _current_number(self):
        """Повертає останнє число у виразі."""
        index = len(self.expression)

        while index > 0 and (
            self.expression[index - 1] in DIGITS
            or self.expression[index - 1] == "."
        ):
            index -= 1

        return self.expression[index:]

    def _operand_start(self):
        """Визначає початок останнього числа з урахуванням мінуса."""
        start = (
            len(self.expression)
            - len(self._current_number())
        )

        if start > 0 and self._is_unary_minus(start - 1):
            start -= 1

        return start

    def _is_unary_minus(self, index):
        return (
            self.expression[index] == "−"
            and (
                index == 0
                or self.expression[index - 1] in "×÷^"
            )
        )

    def _refresh(self):
        if not hasattr(self, "display_label"):
            return

        if self.error:
            text = self.error
            color = self.theme.error
            size = sp(32)
        else:
            text = self.expression or "0"
            color = self.theme.text
            size = self._font_size_for(text)

        self.display_label.text = text
        self.display_label.color = color
        self.display_label.font_size = size

        self.history_label.text = self.history_line

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
