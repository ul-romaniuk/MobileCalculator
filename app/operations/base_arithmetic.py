from decimal import Decimal

from operations.base import BinaryOperation
from operations.errors import CalculatorError, DIVISION_BY_ZERO


class Addition(BinaryOperation):
    symbol = "+"
    priority = 1

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return a + b


class Subtraction(BinaryOperation):
    symbol = "-"
    priority = 1

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return a - b


class Multiplication(BinaryOperation):
    symbol = "*"
    priority = 2

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return a * b


class Division(BinaryOperation):
    symbol = "/"
    priority = 2

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        if b == 0:
            raise CalculatorError(DIVISION_BY_ZERO)

        return a / b


class Power(BinaryOperation):
    symbol = "^"
    priority = 3
    right_associative = True

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        if a == 0 and b < 0:
            raise CalculatorError(DIVISION_BY_ZERO)

        return a ** b