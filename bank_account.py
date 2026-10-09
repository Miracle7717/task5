"""Простая система банковского счёта."""

import math
from numbers import Real


class InvalidAmountError(ValueError):
    """Сумма операции некорректна (не число, нуль, отрицательная, NaN, inf)."""


class InsufficientFundsError(ValueError):
    """На счёте недостаточно средств для выполнения операции."""


class BankAccount:
    """Банковский счёт с владельцем, номером и текущим балансом."""

    def __init__(self, owner, account_number):
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("Имя владельца должно быть непустой строкой")
        if not isinstance(account_number, str) or not account_number.strip():
            raise ValueError("Номер счёта должен быть непустой строкой")

        self._owner = owner.strip()
        self._account_number = account_number.strip()
        self._balance = 0

    # --- свойства только для чтения -------------------------------------
    @property
    def owner(self):
        return self._owner

    @property
    def account_number(self):
        return self._account_number

    @property
    def balance(self):
        return self._balance

    # --- вспомогательные методы -----------------------------------------
    @staticmethod
    def _validate_amount(amount):
        """Сумма должна быть положительным конечным числом (bool не допускается)."""
        if isinstance(amount, bool) or not isinstance(amount, Real):
            raise InvalidAmountError("Сумма должна быть числом")
        if math.isnan(amount) or math.isinf(amount):
            raise InvalidAmountError("Сумма должна быть конечным числом")
        if amount <= 0:
            raise InvalidAmountError("Сумма должна быть больше нуля")

    # --- операции -------------------------------------------------------
    def deposit(self, amount):
        """Пополнить счёт на указанную сумму."""
        self._validate_amount(amount)
        self._balance += amount

    def withdraw(self, amount):
        """Снять со счёта указанную сумму."""
        self._validate_amount(amount)
        if amount > self._balance:
            raise InsufficientFundsError("Недостаточно средств на счёте")
        self._balance -= amount

    def transfer(self, target, amount):
        """Перевести сумму на другой счёт.

        Операция атомарна: если перевод невозможен, оба счёта остаются без изменений.
        """
        if not isinstance(target, BankAccount):
            raise TypeError("Получатель должен быть объектом BankAccount")
        if target is self:
            raise ValueError("Нельзя переводить деньги на тот же самый счёт")
        # Все проверки выполняются до изменения состояния.
        self._validate_amount(amount)
        if amount > self._balance:
            raise InsufficientFundsError("Недостаточно средств на счёте")

        self._balance -= amount
        target._balance += amount

    def get_balance(self):
        """Вернуть текущий баланс."""
        return self._balance

    def is_empty(self):
        """Счёт пуст, если баланс равен нулю."""
        return self._balance == 0

    def __repr__(self):
        return (f"BankAccount(owner={self._owner!r}, "
                f"account_number={self._account_number!r}, balance={self._balance})")