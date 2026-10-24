from decimal import Decimal

from operations.base import UnaryOperation
from operations.errors import CalculatorError, DIVISION_BY_ZERO, NEGATIVE_SQRT


class Square(UnaryOperation):
    symbol = "x²"

    def execute(self, a: Decimal) -> Decimal:
        return a * a


class SquareRoot(UnaryOperation):
    symbol = "√"

    def execute(self, a: Decimal) -> Decimal:
        if a < 0:
            raise CalculatorError(NEGATIVE_SQRT)

        return a.sqrt()


class Reciprocal(UnaryOperation):
    symbol = "1/x"

    def execute(self, a: Decimal) -> Decimal:
        if a == 0:
            raise CalculatorError(DIVISION_BY_ZERO)

        return Decimal(1) / a


class Negation(UnaryOperation):
    symbol = "±"

    def execute(self, a: Decimal) -> Decimal:
        return -a


class Percent(UnaryOperation):
    symbol = "%"

    def execute(self, a: Decimal) -> Decimal:
        return a / Decimal("100")