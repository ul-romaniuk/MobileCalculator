"""Керує діями користувача на екрані калькулятора."""

from decimal import Decimal, InvalidOperation

from model.calculator_model import CalculatorModel
from model.operations.exceptions import CalculatorException


DIGITS = "0123456789"
OPERATORS = "+−×÷^"
KEY_ALIASES = {"x^y": "^"}
UNARY_HISTORY_TEMPLATES = {"x²": "({})²", "√": "√({})", "1/x": "1/({})"}


class CalculatorController:
    """Перетворює натискання клавіш на операції моделі."""

    def __init__(self, model: CalculatorModel):
        """Створює контролер для переданої моделі."""
        self.model = model
        self.on_change = None

    def set_change_callback(self, callback):
        """Реєструє функцію оновлення дисплея після зміни моделі."""
        self.on_change = callback

    def _notify_change(self):
        if self.on_change is not None:
            self.on_change()

    def display_state(self):
        """Повертає стан дисплея для подання."""
        return self.model.display_state()

    def handle_key(self, key):
        """Обробляє натискання клавіші та оновлює дисплей."""
        key = KEY_ALIASES.get(key, key)

        if key in DIGITS:
            self._input_digit(key)
        elif key == ".":
            self._input_dot()
        elif key == "%":
            self._apply_percent()
        elif key in OPERATORS:
            self._input_operator(key)
        elif self.model.supports_unary(key):
            self._apply_unary(key)
        elif key == "=":
            self._evaluate()
        elif key in ("DEL", "⌫"):
            self._delete_last()
        elif key in ("AC", "C"):
            self._reset_state()
        self._notify_change()

    def load_expression(self, expression):
        """Завантажує вираз з історії та оновлює дисплей."""
        self._reset_state()
        self.model.expression = expression
        self._notify_change()

    def clear(self):
        """Скидає поточний вираз, помилку та індикатор результату."""
        self._reset_state()
        self._notify_change()

    def _reset_state(self):
        self.model.expression = ""
        self.model.history_line = ""
        self.model.error = None
        self.model.just_evaluated = False

    def _input_digit(self, digit):
        if self.model.just_evaluated or self.model.error:
            self._reset_state()
        current = self._current_number()
        if current == "0":
            self.model.expression = self.model.expression[:-1] + digit
        else:
            self.model.expression += digit

    def _input_dot(self):
        if self.model.just_evaluated or self.model.error:
            self._reset_state()
        current = self._current_number()
        if "." not in current:
            self.model.expression += "." if current else "0."

    def _input_operator(self, operator):
        model = self.model
        if model.error:
            return
        model.just_evaluated = False
        model.history_line = ""
        if not model.expression:
            if operator == "−":
                model.expression = operator
            return
        last = model.expression[-1]
        if last in OPERATORS:
            if operator == "−" and last in "×÷^":
                model.expression += operator
                return
            base = model.expression.rstrip(OPERATORS)
            if base:
                model.expression = base + operator
        else:
            model.expression += operator

    def _apply_unary(self, symbol):
        model = self.model
        if model.error or not self._current_number():
            return
        start = self._operand_start()
        operand = model.expression[start:]
        try:
            result = model.apply_unary(symbol, Decimal(operand.replace("−", "-")))
        except InvalidOperation:
            return
        except CalculatorException as error:
            model.error = str(error)
            return
        text = self._format(result)
        template = UNARY_HISTORY_TEMPLATES.get(symbol)
        if template:
            model.add_history(template.format(operand), text, recall=text)
        model.expression = model.expression[:start] + text
        model.history_line = ""
        model.just_evaluated = False

    def _apply_percent(self):
        model = self.model
        if model.error or not self._current_number():
            return
        start = self._operand_start()
        operand = model.expression[start:]
        try:
            value = Decimal(operand.replace("−", "-"))
            result = model.apply_unary("%", value)
        except (InvalidOperation, ZeroDivisionError, CalculatorException):
            return
        model.expression = model.expression[:start] + self._format(result)
        model.history_line = ""
        model.just_evaluated = False

    def _delete_last(self):
        if self.model.error:
            self.clear()
            return
        self.model.just_evaluated = False
        self.model.history_line = ""
        self.model.expression = self.model.expression[:-1]

    def _evaluate(self):
        model = self.model
        if not model.expression or model.error or model.just_evaluated:
            return
        expression = model.expression
        try:
            result = model.calculate(expression)
        except CalculatorException as error:
            model.error = str(error)
            return
        text = self._format(result)
        if text != expression:
            model.add_history(expression, text)
        model.history_line = f"{expression} ="
        model.expression = text
        model.just_evaluated = True

    def _format(self, value):
        return self.model.format_result(value).replace("-", "−")

    def _current_number(self):
        expression = self.model.expression
        index = len(expression)
        while index > 0 and (expression[index - 1] in DIGITS or expression[index - 1] == "."):
            index -= 1
        return expression[index:]

    def _operand_start(self):
        start = len(self.model.expression) - len(self._current_number())
        if start > 0 and self._is_unary_minus(start - 1):
            start -= 1
        return start

    def _is_unary_minus(self, index):
        expression = self.model.expression
        return expression[index] == "−" and (index == 0 or expression[index - 1] in "×÷^")
