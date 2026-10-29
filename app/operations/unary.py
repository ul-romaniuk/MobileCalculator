"""Реалізації унарних операцій калькулятора."""

from decimal import Decimal

from operations.base import UnaryOperation
from operations.exceptions import DivisionByZeroException, NegativeSqrtException


class Square(UnaryOperation):
    """Піднесення числа до квадрата."""
    symbol = "x²"

    def execute(self, a: Decimal) -> Decimal:
        """Повертає квадрат числа."""
        return a * a


class SquareRoot(UnaryOperation):
    """Обчислення квадратного кореня."""
    symbol = "√"

    def execute(self, a: Decimal) -> Decimal:
        """Повертає корінь або піднімає CalculatorException для від'ємного числа."""
        if a < 0:
            raise NegativeSqrtException()

        return a.sqrt()


class Reciprocal(UnaryOperation):
    """Обчислення оберненого числа."""
    symbol = "1/x"

    def execute(self, a: Decimal) -> Decimal:
        """Повертає обернене число або піднімає CalculatorException для нуля."""
        if a == 0:
            raise DivisionByZeroException()

        return Decimal(1) / a


class Negation(UnaryOperation):
    """Зміна знака числа."""
    symbol = "±"

    def execute(self, a: Decimal) -> Decimal:
        """Повертає число з протилежним знаком."""
        return -a


class Percent(UnaryOperation):
    """Перетворення числа на відсоткову частку."""
    symbol = "%"

    def execute(self, a: Decimal) -> Decimal:
        """Повертає число, поділене на сто."""
        return a / Decimal("100")
