class CalculatorError(Exception):
    """Помилка обчислення, текст якої можна показати користувачу."""


INVALID_EXPRESSION = "Некоректний вираз"
DIVISION_BY_ZERO = "Ділення на нуль"
CALCULATION_FAILED = "Помилка обчислення"
NEGATIVE_SQRT = "Корінь з від'ємного числа"