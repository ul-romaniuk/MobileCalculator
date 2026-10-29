"""Реалізації базових арифметичних операцій."""

from decimal import Decimal

from model.operations.base import BinaryOperation
from model.operations.exceptions import DivisionByZeroException


class Addition(BinaryOperation):
    """Додавання двох чисел."""
    symbol = "+"
    priority = 1

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Повертає суму чисел."""
        return a + b


class Subtraction(BinaryOperation):
    """Віднімання другого числа від першого."""
    symbol = "-"
    priority = 1

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Повертає різницю чисел."""
        return a - b


class Multiplication(BinaryOperation):
    """Множення двох чисел."""
    symbol = "*"
    priority = 2

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Повертає добуток чисел."""
        return a * b


class Division(BinaryOperation):
    """Ділення першого числа на друге."""
    symbol = "/"
    priority = 2

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Повертає частку або піднімає CalculatorException при діленні на нуль."""
        if b == 0:
            raise DivisionByZeroException()

        return a / b


class Power(BinaryOperation):
    """Піднесення числа до степеня."""
    symbol = "^"
    priority = 3
    right_associative = True

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Повертає степінь або піднімає CalculatorException для нульової основи."""
        if a == 0 and b < 0:
            raise DivisionByZeroException()

        return a ** b
