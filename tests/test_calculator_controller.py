"""Перевірки клавіатурних сценаріїв контролера калькулятора."""

from models.calculator_model import CalculatorModel
from controllers.calculator_controller import CalculatorController
from operations.calculator import Calculator


class MemoryHistory:
    """Історія в пам'яті для ізольованих тестів контролера."""

    def __init__(self):
        self.records = []

    def add(self, expression, result, recall=None):
        self.records.append((expression, result, recall or expression))


def make_controller():
    """Створює контролер без файлового сховища."""
    return CalculatorController(CalculatorModel(Calculator(), MemoryHistory()))


def press(controller, *keys):
    """Послідовно передає контролеру натискання клавіш."""
    for key in keys:
        controller.handle_key(key)


def test_calculate_and_store_history():
    """Обчислює вираз і додає результат до історії."""
    controller = make_controller()
    press(controller, "2", "+", "3", "=")

    assert controller.display_state() == ("5", "2+3 =", None)
    assert controller.model.history.records == [("2+3", "5", "2+3")]


def test_unary_and_percent_operations():
    """Зберігає результати унарної операції та відсотка."""
    controller = make_controller()
    press(controller, "5", "x²")
    assert controller.display_state()[0] == "25"
    press(controller, "AC", "5", "0", "%")
    assert controller.display_state()[0] == "0.5"


def test_calculation_error_is_shown_and_clearable():
    """Показує помилку ділення на нуль і очищає її кнопкою AC."""
    controller = make_controller()
    press(controller, "5", "÷", "0", "=")
    assert controller.display_state()[2] == "Ділення на нуль"
    press(controller, "AC")
    assert controller.display_state() == ("", "", None)


def test_load_expression_from_history():
    """Завантажує вибраний вираз і скидає попередній стан дисплея."""
    controller = make_controller()
    press(controller, "9", "=")
    controller.load_expression("2+3")

    assert controller.display_state() == ("2+3", "", None)
