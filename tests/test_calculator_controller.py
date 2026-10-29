"""Перевірки клавіатурних сценаріїв контролера калькулятора."""

from model.calculator_model import CalculatorModel
from controller.calculator_controller import CalculatorController
from model.operations.calculator import Calculator


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
    assert controller.model.history.records == [("(5)²", "25", "25")]
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


def test_key_alias_for_power_and_result_restarts_expression():
    """Підтримує старий псевдонім степеня та новий ввід після результату."""
    controller = make_controller()
    press(controller, "2", "x^y", "3", "=")
    assert controller.display_state() == ("8", "2^3 =", None)

    press(controller, "4")
    assert controller.display_state() == ("4", "", None)


def test_leading_zero_decimal_and_duplicate_decimal():
    """Не додає нулі попереду числа й забороняє дві коми в одному операнді."""
    controller = make_controller()
    press(controller, "0", "0", ".", "5", ".", "2")
    assert controller.display_state()[0] == "0.52"


def test_operator_replacement_and_unary_minus():
    """Замінює оператор наприкінці виразу й дозволяє мінус після множення."""
    controller = make_controller()
    press(controller, "8", "+", "×", "−", "2", "=")
    assert controller.display_state() == ("−16", "8×−2 =", None)


def test_backspace_alias_and_clear_alias():
    """Видаляє символ клавішею Backspace та очищає стан клавішею C."""
    controller = make_controller()
    press(controller, "1", "2", "⌫")
    assert controller.display_state()[0] == "1"

    press(controller, "C")
    assert controller.display_state() == ("", "", None)


def test_clear_after_error_and_delete_after_error():
    """Очищає помилку кнопкою DEL або AC."""
    controller = make_controller()
    press(controller, "5", "÷", "0", "=")
    press(controller, "DEL")
    assert controller.display_state() == ("", "", None)

    press(controller, "5", "÷", "0", "=", "AC")
    assert controller.display_state() == ("", "", None)


def test_duplicate_evaluation_does_not_add_duplicate_history():
    """Повторне натискання дорівнює не перераховує результат."""
    controller = make_controller()
    press(controller, "2", "+", "3", "=", "=")
    assert controller.model.history.records == [("2+3", "5", "2+3")]


def test_negative_unary_and_percent():
    """Обробляє унарний мінус, зміну знака та відсоток."""
    controller = make_controller()
    press(controller, "−", "5", "±")
    assert controller.display_state()[0] == "5"

    press(controller, "%")
    assert controller.display_state()[0] == "0.05"


def test_invalid_key_is_ignored_but_view_is_notified():
    """Ігнорує невідому клавішу та сповіщає підписника про подію."""
    controller = make_controller()
    notifications = []
    controller.set_change_callback(lambda: notifications.append(True))

    controller.handle_key("unknown")

    assert controller.display_state() == ("", "", None)
    assert notifications == [True]


def test_sqrt_error_is_rendered_and_recovers_on_input():
    """Показує помилку від'ємного кореня й починає новий ввід після неї."""
    controller = make_controller()
    press(controller, "−", "9", "√")

    assert controller.display_state()[2] == "Корінь з від'ємного числа"

    press(controller, "4")
    assert controller.display_state() == ("4", "", None)


def test_empty_evaluation_and_delete_are_safe():
    """Не створює помилки або історії для порожнього виразу."""
    controller = make_controller()
    press(controller, "=", "DEL")

    assert controller.display_state() == ("", "", None)
    assert controller.model.history.records == []


def test_plus_at_start_is_ignored_and_minus_is_accepted():
    """Ігнорує початковий плюс і приймає початковий мінус."""
    controller = make_controller()
    press(controller, "+")
    assert controller.display_state()[0] == ""

    press(controller, "−", "3", "=")
    assert controller.display_state() == ("−3", "−3 =", None)
