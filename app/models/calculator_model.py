"""Модель стану калькулятора та його залежностей."""

from operations.calculator import Calculator
from storage.history import History


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
