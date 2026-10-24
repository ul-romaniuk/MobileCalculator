from abc import ABC, abstractmethod
from decimal import Decimal


class BinaryOperation(ABC):
    """Базова операція над двома числами (a + b, a ^ b ...).

    symbol            - символ, яким операція позначається у виразі.
    priority          - чим більше число, тим раніше виконується операція.
    right_associative - True, якщо a ^ b ^ c = a ^ (b ^ c).
    """

    symbol: str
    priority: int
    right_associative: bool = False

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        ...


class UnaryOperation(ABC):
    """Базова операція над одним числом (x², √x, 1/x ...).

    symbol - текст кнопки, яка запускає цю операцію.
    """

    symbol: str

    @abstractmethod
    def execute(self, a: Decimal) -> Decimal:
        ...