"""Абстрактні типи арифметичних операцій."""

from abc import ABC, abstractmethod
from decimal import Decimal


class BinaryOperation(ABC):
    """Базова операція над двома числами.

    Атрибути визначають символ, пріоритет і напрямок асоціативності.
    """

    symbol: str
    priority: int
    right_associative: bool = False

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Виконує бінарну операцію над двома числами."""
        ...


class UnaryOperation(ABC):
    """Базова операція над одним числом."""

    symbol: str

    @abstractmethod
    def execute(self, a: Decimal) -> Decimal:
        """Виконує унарну операцію над числом."""
        ...
