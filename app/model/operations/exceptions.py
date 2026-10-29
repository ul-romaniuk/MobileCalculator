"""Винятки, що виникають під час обчислення виразів."""


class CalculatorException(Exception):
    """Базовий виняток калькулятора."""


class InvalidExpressionException(CalculatorException):
    """Некоректний арифметичний вираз."""

    def __init__(self, message="Некоректний вираз"):
        super().__init__(message)


class DivisionByZeroException(CalculatorException):
    """Спроба ділення на нуль."""

    def __init__(self, message="Ділення на нуль"):
        super().__init__(message)


class CalculationFailedException(CalculatorException):
    """Помилка під час виконання обчислення."""

    def __init__(self, message="Помилка обчислення"):
        super().__init__(message)


class NegativeSqrtException(CalculatorException):
    """Спроба знайти корінь від'ємного числа."""

    def __init__(self, message="Корінь з від'ємного числа"):
        super().__init__(message)
