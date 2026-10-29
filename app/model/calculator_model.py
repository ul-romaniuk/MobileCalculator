"""Модель стану калькулятора та його залежностей."""

from decimal import Decimal

from model.operations.calculator import Calculator
from model.storage.history import History


class CalculatorModel:
    """Зберігає стан поточного обчислення та доступ до доменних даних."""

    def __init__(self, calculator: Calculator, history: History):
        """Створює модель з обчислювачем і сховищем історії."""
        self.calculator = calculator
        self.history = history
        self.expression = ""
        self.history_line = ""
        self.error = None
        self.just_evaluated = False

    def display_state(self):
        """Повертає значення, які потрібні дисплею."""
        return self.expression, self.history_line, self.error

    def calculate(self, expression: str) -> Decimal:
        """Обчислює вираз через доменний обчислювач."""
        return self.calculator.calculate(expression)

    def apply_unary(self, symbol: str, value: Decimal) -> Decimal:
        """Застосовує унарну операцію до числа."""
        return self.calculator.apply_unary(symbol, value)

    def supports_unary(self, symbol: str) -> bool:
        """Перевіряє, чи існує унарна операція з таким символом."""
        return symbol in self.calculator.unary_operations

    def format_result(self, value: Decimal) -> str:
        """Повертає відформатований результат обчислення."""
        return self.calculator.format_result(value)

    def add_history(self, expression: str, result: str, recall: str | None = None) -> None:
        """Додає результат до історії."""
        self.history.add(expression, result, recall)
