"""Перевірки арифметики, помилок і формату результату."""

from decimal import Decimal

import pytest

from app.operations.calculator import Calculator
from app.config import settings
from operations.exceptions import (
    CalculatorException,
    InvalidExpressionException,
    DivisionByZeroException,
    NegativeSqrtException,
)


@pytest.fixture
def calculator():
    return Calculator()


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2+3", Decimal("5")),
        ("10-4", Decimal("6")),
        ("6*7", Decimal("42")),
        ("20/5", Decimal("4")),
        ("2+3*4", Decimal("14")),
    ],
)
def test_calculate(calculator, expression, expected):
    if expected is None:
        pytest.skip("Цей випадок не є арифметичним виразом")
    assert calculator.calculate(expression) == expected


def test_power_is_right_associative(calculator):
    assert calculator.calculate("2^3^2") == Decimal("512")


def test_negative_number(calculator):
    assert calculator.calculate("-5+2") == Decimal("-3")


def test_decimal_comma(calculator):
    assert calculator.calculate("2,5+1,5") == Decimal("4.0")


def test_unicode_operators(calculator):
    assert calculator.calculate("2×3") == Decimal("6")
    assert calculator.calculate("8÷2") == Decimal("4")

def test_power_100(calculator):
    result = calculator.calculate("2^100")
    formatted = Calculator.format_result(result)

    assert result > 0
    assert "e+" in formatted.lower()
    assert len(formatted) <= settings.max_display_length


def test_power_1000(calculator):
    result = calculator.calculate("2^1000")
    assert result > 0
    assert len(Calculator.format_result(result)) <= settings.max_display_length


def test_power_extremely_large(calculator):
    with pytest.raises(CalculatorException):
        calculator.calculate("2^100000000000000")


@pytest.mark.parametrize(
    "expression",
    [
        "",
        "5+",
        "+5",
        "2++3",
        "abc",
        "1..2",
    ],
)
def test_invalid_expression(calculator, expression):
    with pytest.raises(CalculatorException) as error:
        calculator.calculate(expression)

    assert str(error.value) == str(InvalidExpressionException())


def test_division_by_zero(calculator):
    with pytest.raises(CalculatorException) as error:
        calculator.calculate("5/0")

    assert str(error.value) == str(DivisionByZeroException())


@pytest.mark.parametrize(
    ("symbol", "value", "expected"),
    [
        ("x²", "5", "25"),
        ("√", "49", "7"),
        ("1/x", "4", "0.25"),
        ("±", "5", "-5"),
        ("%", "50", "0.5"),
    ],
)
def test_unary_operations(calculator, symbol, value, expected):
    result = calculator.apply_unary(symbol, Decimal(value))
    assert result == Decimal(expected)


def test_square_root_of_negative_number(calculator):
    with pytest.raises(CalculatorException) as error:
        calculator.apply_unary("√", Decimal("-9"))

    assert str(error.value) == str(NegativeSqrtException())


def test_reciprocal_of_zero(calculator):
    with pytest.raises(CalculatorException) as error:
        calculator.apply_unary("1/x", Decimal("0"))

    assert str(error.value) == str(DivisionByZeroException())


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("0", "0"),
        ("-0", "0"),
        ("42", "42"),
        ("123.4500", "123.45"),
        ("0.33333333333333333333", "0.3333333333"),
        ("10000000000000000", "1e+16"),
        ("100000000000000000000", "1e+20"),
        ("0.000000001", "1e-9"),
    ],
)
def test_format_result(value, expected):
    result = Calculator.format_result(Decimal(value))
    assert result == expected

