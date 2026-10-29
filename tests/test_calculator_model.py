"""Перевірки стану та доменних методів моделі калькулятора."""

from decimal import Decimal

from model.calculator_model import CalculatorModel
from model.operations.calculator import Calculator


class HistorySpy:
    """Фіксує записи, передані моделлю до історії."""

    def __init__(self):
        self.records = []

    def add(self, expression, result, recall=None):
        self.records.append((expression, result, recall))


def test_model_initial_state_and_display_state():
    """Створює початковий стан і віддає його для відображення."""
    model = CalculatorModel(Calculator(), HistorySpy())

    assert model.display_state() == ("", "", None)
    assert model.just_evaluated is False


def test_model_delegates_calculation_and_unary_operations():
    """Надає контролеру операції обчислення через модель."""
    model = CalculatorModel(Calculator(), HistorySpy())

    assert model.calculate("2+3") == Decimal("5")
    assert model.apply_unary("x²", Decimal("4")) == Decimal("16")
    assert model.supports_unary("√")
    assert not model.supports_unary("unknown")
    assert model.format_result(Decimal("0.5000")) == "0.5"


def test_model_adds_history_entry():
    """Передає результат і значення повторного введення в історію."""
    history = HistorySpy()
    model = CalculatorModel(Calculator(), history)

    model.add_history("2+3", "5", recall="5")

    assert history.records == [("2+3", "5", "5")]
