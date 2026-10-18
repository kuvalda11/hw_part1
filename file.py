from abc import ABC, abstractmethod
import uuid

class AccountFrozenError(Exception):
    pass

class AccountClosedError(Exception):
    pass

class InvalidOperationError(Exception):
    pass

class InsufficientFundsError(Exception):
    pass


class AbstractAccount(ABC):

    VALID_STATUSES = ('active', 'frozen', 'closed')

    def __init__(self, owner: str, acc_id: str, balance: float = 0.0, status: str = 'active'):
        self.owner = owner
        self.acc_id = acc_id
        self._balance = balance
        self.status = status

    @abstractmethod
    def deposit(self, amount: float):
        pass

    @abstractmethod
    def withdraw(self, amount: float):
        pass

    @abstractmethod
    def get_account_info(self) -> dict:
        pass


class BankAccount(AbstractAccount):

    VALID_CURRENCIES = ('RUB', 'USD', 'EUR', 'KZT', 'CNY')

    def __init__(self, owner: str, balance: float = 0.0,
                     acc_id: str = None, status: str = "active",
                     currency: str = "RUB"):

        if not owner or not isinstance(owner, str) or len(owner.strip()) < 2:
            raise ValueError("Владелец должен иметь минимум 2 символа")

        if not isinstance(balance, (int, float)) or balance < 0:
            raise ValueError("Баланс не может быть отрицательным")

        if currency not in self.VALID_CURRENCIES:
            raise ValueError(f"Недопустимая валюта. Допустимые: {self.VALID_CURRENCIES}")

        if status not in self.VALID_STATUSES:
            raise ValueError(f"Недопустимый статус. Допустимые: {self.VALID_STATUSES}")

        if acc_id is None:
            acc_id = uuid.uuid4().hex[:8]

        super().__init__(owner, acc_id, balance, status)
        self.currency = currency



    def deposit(self, amount: float):
        if self.status == "frozen":
            raise AccountFrozenError("Счёт заморожен, операции недоступны")

        if self.status == "closed":
            raise AccountClosedError("Счёт закрыт, операции недоступны")

        if not isinstance(amount, (int, float)) or amount <= 0:
            raise InvalidOperationError("Сумма пополнения должна быть положительным числом")

        self._balance += amount

    def withdraw(self, amount: float):
        if self.status == "frozen":
            raise AccountFrozenError("Счёт заморожен, операции недоступны")

        if self.status == "closed":
            raise AccountClosedError("Счёт закрыт, операции недоступны")

        if not isinstance(amount, (int, float)) or amount <= 0:
            raise InvalidOperationError("Сумма снятия должна быть положительным числом")

        if self._balance < amount:
            raise InsufficientFundsError(f"Недостаточно средств. Баланс: {self._balance}, попытка снять: {amount}")

        self._balance -= amount

    def get_account_info(self) -> dict:
        return {
            "owner": self.owner,
            "acc_id": self.acc_id,
            "balance": self._balance,
            "status": self.status,
            "currency": self.currency
        }

    def __str__(self):
        return (
            f"Тип счета: {self.__class__.__name__} | "
            f"Клиент: {self.owner} | "
            f"Последние 4 цифры счета {self.acc_id[-4:]} | "
            f"Статус: {self.status} | "
            f"Средства: {self._balance} {self.currency}"
        )


if __name__ == "__main__":
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ БАНКОВСКОГО СЧЁТА")
    print("=" * 60)

    # Создание активного и замороженного счёта
    print("\n[1] Создание счетов")
    print("-" * 60)
    active_account = BankAccount("Олег Монгол", 1000.0)
    frozen_account = BankAccount("Пётр Петров", 500.0, status="frozen", currency="USD")

    print(f"Активный счёт:   {active_account}")
    print(f"Замороженный счёт: {frozen_account}")

    # Валидное пополнение и снятие
    print("\n[2] Валидные операции над активным счётом")
    print("-" * 60)
    print(f"Исходный баланс: {active_account._balance} {active_account.currency}")

    active_account.deposit(500)
    print(f"После пополнения на 500: {active_account._balance} {active_account.currency}")

    active_account.withdraw(200)
    print(f"После снятия 200: {active_account._balance} {active_account.currency}")

    # Попытки операций над замороженным счётом
    print("\n[3] Попытки операций над замороженным счётом")
    print("-" * 60)
    try:
        frozen_account.deposit(100)
    except AccountFrozenError as e:
        print(f"Пополнение отклонено: {e}")

    try:
        frozen_account.withdraw(50)
    except AccountFrozenError as e:
        print(f"Снятие отклонено: {e}")

    # Прочие ошибки
    print("\n[4] Проверка прочих ошибок")
    print("-" * 60)
    try:
        active_account.withdraw(999999)
    except InsufficientFundsError as e:
        print(f"Недостаточно средств: {e}")

    try:
        active_account.deposit(-100)
    except InvalidOperationError as e:
        print(f"Некорректная операция: {e}")

    try:
        active_account.deposit("сто")
    except InvalidOperationError as e:
        print(f"Некорректная операция: {e}")

    # Информация о счёте
    print("\n[5] Полная информация о счёте")
    print("-" * 60)
    info = active_account.get_account_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)
