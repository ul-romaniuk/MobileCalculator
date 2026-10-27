from decimal import Decimal, InvalidOperation

from operations.base import BinaryOperation, UnaryOperation
from operations.base_arithmetic import (
    Addition,
    Subtraction,
    Multiplication,
    Division,
    Power,
)
from operations.errors import (
    CalculatorError,
    INVALID_EXPRESSION,
    CALCULATION_FAILED,
    TOO_LARGE,
)
from operations.unary import (
    Square,
    SquareRoot,
    Reciprocal,
    Negation,
    Percent,
)

SYMBOL_ALIASES = {"×": "*", "÷": "/", "−": "-", ",": "."}

# Результат має бути менший за 10^16, щоб числа вміщалися на екрані
MAX_ADJUSTED_EXPONENT = 15


class Calculator:
    """Розбирає вираз і обчислює його з урахуванням пріоритету операцій.

    Використовує Decimal, тому 0.1 + 0.2 дає рівно 0.3.
    Підтримує унарний мінус ("-5+3", "5*-3") і степінь ("2^3^2").
    Одномісні операції (x², √, 1/x, ±) викликаються через apply_unary().
    """

    RESULT_PRECISION = Decimal("1e-10")

    def __init__(self):
        self.operations: dict[str, BinaryOperation] = {
            operation.symbol: operation
            for operation in (Addition(), Subtraction(), Multiplication(), Division(), Power())
        }
        self.unary_operations: dict[str, UnaryOperation] = {
            operation.symbol: operation
            for operation in (
                Square(),
                SquareRoot(),
                Reciprocal(),
                Negation(),
                Percent(),
            )
        }
        self._priorities = sorted(
            {operation.priority for operation in self.operations.values()},
            reverse=True,
        )


    def calculate(self, expression: str) -> Decimal:
        try:
            numbers, operators = self._parse(expression)
            return self._check_size(self._evaluate(numbers, operators))
        except ArithmeticError:
            raise CalculatorError(CALCULATION_FAILED) from None

    def apply_unary(self, symbol: str, value: Decimal) -> Decimal:
        try:
            return self._check_size(self.unary_operations[symbol].execute(value))
        except ArithmeticError:
            raise CalculatorError(CALCULATION_FAILED) from None

    @classmethod
    def format_result(cls, value: Decimal) -> str:
        try:
            value = value.quantize(cls.RESULT_PRECISION)
        except InvalidOperation:
            pass

        if value == 0:
            return "0"

        return format(value.normalize(), "f")


    def _parse(self, expression: str) -> tuple[list[Decimal], list[str]]:
        numbers: list[Decimal] = []
        operators: list[str] = []

        buffer = ""
        negative = False
        expect_operand = True

        for raw_symbol in expression:
            symbol = SYMBOL_ALIASES.get(raw_symbol, raw_symbol)

            if symbol.isspace():
                continue

            if symbol.isdigit() or symbol == ".":
                buffer += symbol

            elif symbol in self.operations:
                if buffer:
                    numbers.append(self._to_number(buffer, negative))
                    buffer = ""
                    negative = False
                    expect_operand = False

                if expect_operand:
                    if symbol == "-" and not negative:
                        negative = True
                    else:
                        raise CalculatorError(INVALID_EXPRESSION)
                else:
                    operators.append(symbol)
                    expect_operand = True

            else:
                raise CalculatorError(INVALID_EXPRESSION)

        if buffer:
            numbers.append(self._to_number(buffer, negative))

        if not numbers or len(numbers) != len(operators) + 1:
            raise CalculatorError(INVALID_EXPRESSION)

        return numbers, operators

    @staticmethod
    def _to_number(text: str, negative: bool) -> Decimal:
        try:
            value = Decimal(text)
        except InvalidOperation:
            raise CalculatorError(INVALID_EXPRESSION) from None

        return -value if negative else value


    def _evaluate(self, numbers: list[Decimal], operators: list[str]) -> Decimal:
        for priority in self._priorities:
            while indexes := self._operator_indexes(operators, priority):
                first = self.operations[operators[indexes[0]]]
                index = indexes[-1] if first.right_associative else indexes[0]

                operation = self.operations[operators.pop(index)]
                numbers[index:index + 2] = [operation.execute(numbers[index], numbers[index + 1])]

        return numbers[0]

    def _operator_indexes(self, operators: list[str], priority: int) -> list[int]:
        """Позиції операторів із заданим пріоритетом."""
        return [
            index
            for index, symbol in enumerate(operators)
            if self.operations[symbol].priority == priority
        ]

    @staticmethod
    def _check_size(value: Decimal) -> Decimal:
        if value.is_finite() and value.adjusted() > MAX_ADJUSTED_EXPONENT:
            raise CalculatorError(TOO_LARGE)

        return value