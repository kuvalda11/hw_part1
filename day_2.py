from day_1 import (
    BankAccount,
    AccountFrozenError,
    AccountClosedError,
    InvalidOperationError,
    InsufficientFundsError
)
import math


class SavingsAccount(BankAccount):
    def __init__(self, owner: str, balance: float = 0.0, acc_id: str = None,
                 status: str = "active", currency: str = "RUB",
                 min_balance: float = 10000.0, monthly_interest_rate: float = 0.05):

        super().__init__(owner, balance, acc_id, status, currency)

        if (isinstance(min_balance, bool) or not isinstance(min_balance, (int, float))
                or not math.isfinite(min_balance) or min_balance < 0):
            raise ValueError("Минимальный баланс должен быть неотрицательным конечным числом")

        if (isinstance(monthly_interest_rate, bool) or not isinstance(monthly_interest_rate, (int, float))
                or not math.isfinite(monthly_interest_rate) or monthly_interest_rate < 0):
            raise ValueError("Ставка должна быть неотрицательным конечным числом")

        self.min_balance = min_balance
        self.monthly_interest_rate = monthly_interest_rate

    def withdraw(self, amount: float):
        super().withdraw(amount)

        if self._balance < self.min_balance:
            self._balance += amount
            raise InvalidOperationError(f"Нельзя снять: баланс упадёт ниже минимального ({self.min_balance})")

    def apply_monthly_interest(self):
        self._balance += self._balance * self.monthly_interest_rate

    def get_account_info(self) -> dict:
        info = super().get_account_info()
        info["min_balance"] = self.min_balance
        info["monthly_interest_rate"] = self.monthly_interest_rate
        return info

    def __str__(self):
        base = super().__str__()
        return f"{base} | Мин. остаток: {self.min_balance} | Ставка: {self.monthly_interest_rate * 100}%"


class PremiumAccount(BankAccount):
    def __init__(self, owner: str, balance: float = 0.0, acc_id: str = None,
                 status: str = "active", currency: str = "RUB",
                 overdraft_limit: float = 50000.0, fixed_fee: float = 50.0):

        super().__init__(owner, balance, acc_id, status, currency)

        if (isinstance(overdraft_limit, bool) or not isinstance(overdraft_limit, (int, float))
                or not math.isfinite(overdraft_limit) or overdraft_limit < 0):
            raise ValueError("Лимит овердрафта должен быть неотрицательным конечным числом")

        if (isinstance(fixed_fee, bool) or not isinstance(fixed_fee, (int, float))
                or not math.isfinite(fixed_fee) or fixed_fee < 0):
            raise ValueError("Комиссия должна быть неотрицательным конечным числом")

        self.overdraft_limit = overdraft_limit
        self.fixed_fee = fixed_fee

    def withdraw(self, amount: float):

        if self.status == "frozen":
            raise AccountFrozenError("Счёт заморожен, операции недоступны")
        if self.status == "closed":
            raise AccountClosedError("Счёт закрыт, операции недоступны")

        if (isinstance(amount, bool) or not isinstance(amount, (int, float))
                or not math.isfinite(amount) or amount <= 0):
            raise InvalidOperationError("Сумма снятия должна быть положительным конечным числом")

        total_withdrawal = amount + self.fixed_fee
        if self._balance - total_withdrawal < -self.overdraft_limit:
            raise InsufficientFundsError(
                f"Превышен лимит овердрафта. Баланс: {self._balance}, "
                f"попытка снять: {total_withdrawal} (включая комиссию {self.fixed_fee}), "
                f"лимит овердрафта: {self.overdraft_limit}"
            )

        self._balance -= total_withdrawal

    def get_account_info(self) -> dict:
        info = super().get_account_info()
        info["overdraft_limit"] = self.overdraft_limit
        info["fixed_fee"] = self.fixed_fee
        return info

    def __str__(self):
        base = super().__str__()
        return f"{base} | Овердрафт: {self.overdraft_limit} | Комиссия: {self.fixed_fee}"


class InvestmentAccount(BankAccount):
    VALID_ASSETS = ("stocks", "bonds", "etf")

    def __init__(self, owner: str, balance: float = 0.0, acc_id: str = None,
                 status: str = "active", currency: str = "RUB",
                 portfolio: dict = None):

        super().__init__(owner, balance, acc_id, status, currency)

        if portfolio is None:
            self.portfolio = {"stocks": 0, "bonds": 0, "etf": 0}
        else:
            if not isinstance(portfolio, dict):
                raise ValueError("Портфель должен быть словарём")

            for asset_type, amount in portfolio.items():
                if asset_type not in self.VALID_ASSETS:
                    raise ValueError(
                        f"Недопустимый тип актива: {asset_type}. "
                        f"Допустимые: {self.VALID_ASSETS}"
                    )
                if (isinstance(amount, bool) or not isinstance(amount, (int, float))
                        or not math.isfinite(amount) or amount < 0):
                    raise ValueError(
                        f"Сумма в {asset_type} должна быть неотрицательным конечным числом"
                    )

            self.portfolio = portfolio.copy()

    def invest(self, amount: float, asset_type: str):

        if self.status == "frozen":
            raise AccountFrozenError("Счёт заморожен, операции недоступны")
        if self.status == "closed":
            raise AccountClosedError("Счёт закрыт, операции недоступны")

        if asset_type not in self.VALID_ASSETS:
            raise InvalidOperationError(
                f"Недопустимый тип актива: {asset_type}. "
                f"Допустимые: {self.VALID_ASSETS}"
            )

        if (isinstance(amount, bool) or not isinstance(amount, (int, float))
                or not math.isfinite(amount) or amount <= 0):
            raise InvalidOperationError("Сумма инвестиции должна быть положительным конечным числом")

        if self._balance < amount:
            raise InsufficientFundsError(f"Недостаточно средств. Баланс: {self._balance}")

        self._balance -= amount
        self.portfolio[asset_type] += amount

    def divest(self, amount: float, asset_type: str):
        """Вывести деньги из портфеля в баланс."""

        if self.status == "frozen":
            raise AccountFrozenError("Счёт заморожен, операции недоступны")
        if self.status == "closed":
            raise AccountClosedError("Счёт закрыт, операции недоступны")

        if asset_type not in self.VALID_ASSETS:
            raise InvalidOperationError(
                f"Недопустимый тип актива: {asset_type}. "
                f"Допустимые: {self.VALID_ASSETS}"
            )

        if (isinstance(amount, bool) or not isinstance(amount, (int, float))
                or not math.isfinite(amount) or amount <= 0):
            raise InvalidOperationError(
                "Сумма вывода должна быть положительным конечным числом"
            )

        if self.portfolio[asset_type] < amount:
            raise InsufficientFundsError(
                f"Недостаточно средств в {asset_type}. "
                f"Доступно: {self.portfolio[asset_type]}"
            )

        self.portfolio[asset_type] -= amount
        self._balance += amount

    def project_yearly_growth(self, growth_rates: dict) -> float:

        if not isinstance(growth_rates, dict):
            raise InvalidOperationError("growth_rates должен быть словарём")

        total_growth = 0
        for asset_type, amount in self.portfolio.items():
            if asset_type in growth_rates:
                rate = growth_rates[asset_type]
                if (isinstance(rate, bool) or not isinstance(rate, (int, float)) or not math.isfinite(rate)):
                    raise InvalidOperationError(f"Ставка для {asset_type} должна быть конечным числом")

                total_growth += amount * rate

        return total_growth

    def withdraw(self, amount: float):
        super().withdraw(amount)

    def get_account_info(self) -> dict:
        info = super().get_account_info()
        info["portfolio"] = self.portfolio.copy()
        info["total_invested"] = sum(self.portfolio.values())
        return info

    def __str__(self):
        base = super().__str__()
        portfolio_items = [f"{k}={v}" for k, v in self.portfolio.items()]
        return f"{base} | Портфель: {', '.join(portfolio_items)}"


if __name__ == "__main__":
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ПРОДВИНУТЫХ БАНКОВСКИХ СЧЕТОВ")
    print("=" * 60)

    # ============================================================
    # [1] Создание счетов
    # ============================================================
    print("\n[1] Создание счетов")
    print("-" * 60)

    savings = SavingsAccount("Олег Монгол", 50000.0, min_balance=10000.0, monthly_interest_rate=0.05)
    premium = PremiumAccount("Губка Боб", 100000.0, overdraft_limit=50000.0, fixed_fee=100.0)
    investment = InvestmentAccount("Алло Бизнес", 500000.0)

    print(f"Savings:    {savings}")
    print(f"Premium:    {premium}")
    print(f"Investment: {investment}")

    # ============================================================
    # [2] Операции над SavingsAccount
    # ============================================================
    print("\n[2] Операции над накопительным счётом")
    print("-" * 60)

    savings.deposit(20000)
    print(f"После пополнения на 20000: {savings._balance}")  # 70000

    savings.withdraw(50000)
    print(f"После снятия 50000: {savings._balance}")  # 20000

    # Попытка снять так, чтобы баланс упал ниже min_balance (10000)
    print("\nПопытка снять 15000 (останется 5000 < 10000):")
    try:
        savings.withdraw(15000)
    except InvalidOperationError as e:
        print(f"Отклонено: {e}")
    print(f"Баланс после попытки: {savings._balance}")  # 20000 (не изменился)

    # Начисление процентов
    savings.apply_monthly_interest()
    print(f"\nПосле начисления 5%: {savings._balance}")  # 21000

    # ============================================================
    # [3] Операции над PremiumAccount
    # ============================================================
    print("\n[3] Операции над премиальным счётом")
    print("-" * 60)

    premium.withdraw(5000)
    print(f"После снятия 5000 (+100 комиссия): {premium._balance}")  # 94900

    # Снятие с уходом в овердрафт
    premium.withdraw(120000)
    print(f"После снятия 120000 (+100 комиссия): {premium._balance}")  # -25200 (ушли в минус)

    # Попытка превысить лимит овердрафта
    print("\nПопытка превысить лимит овердрафта:")
    try:
        premium.withdraw(100000)
    except InsufficientFundsError as e:
        print(f"Отклонено: {e}")
    print(f"Баланс после попытки: {premium._balance}")  # -25200 (не изменился)

    # ============================================================
    # [4] Операции над InvestmentAccount
    # ============================================================
    print("\n[4] Операции над инвестиционным счётом")
    print("-" * 60)

    # Инвестиции
    investment.invest(200000, "stocks")
    investment.invest(150000, "bonds")
    investment.invest(100000, "etf")
    print(f"После инвестиций: {investment._balance}")  # 50000
    print(f"Портфель: {investment.portfolio}")

    # Попытка инвестировать больше, чем есть на балансе
    print("\nПопытка инвестировать 100000 (на балансе только 50000):")
    try:
        investment.invest(100000, "stocks")
    except InsufficientFundsError as e:
        print(f"Отклонено: {e}")

    # Попытка инвестировать в недопустимый актив
    print("\nПопытка инвестировать в 'crypto' (недопустимый тип):")
    try:
        investment.invest(10000, "crypto")
    except InvalidOperationError as e:
        print(f"Отклонено: {e}")

    # Прогноз прироста
    growth_rates = {"stocks": 0.10, "bonds": 0.04, "etf": 0.07}
    expected_growth = investment.project_yearly_growth(growth_rates)
    print(f"\nОжидаемый годовой прирост: {expected_growth}")
    # = 200000*0.10 + 150000*0.04 + 100000*0.07 = 20000 + 6000 + 7000 = 33000

    # Вывод из портфеля
    investment.divest(50000, "stocks")
    print(f"\nПосле вывода 50000 из stocks: {investment._balance}")  # 100000
    print(f"Портфель: {investment.portfolio}")

    # Попытка вывести больше, чем есть в активе
    print("\nПопытка вывести 200000 из bonds (есть только 150000):")
    try:
        investment.divest(200000, "bonds")
    except InsufficientFundsError as e:
        print(f"Отклонено: {e}")

    # Снятие с баланса (работает как обычный счёт)
    investment.withdraw(30000)
    print(f"\nПосле снятия 30000 с баланса осталось: {investment._balance}")  # 70000

    # ============================================================
    # [5] Замороженные счета
    # ============================================================
    print("\n[5] Замороженные счета")
    print("-" * 60)

    # Замороженные версии каждого типа
    frozen_savings = SavingsAccount("Замороженный", 50000.0, status="frozen")
    frozen_premium = PremiumAccount("Замороженный", 50000.0, status="frozen")
    frozen_investment = InvestmentAccount("Замороженный", 50000.0, status="frozen")

    print("\nПопытки снятия с замороженных счетов:")
    for name, account in [("Savings", frozen_savings),
                          ("Premium", frozen_premium),
                          ("Investment", frozen_investment)]:
        try:
            account.withdraw(1000)
        except AccountFrozenError as e:
            print(f"{name}: {e}")

    print("\nПопытка инвестировать с замороженного счёта:")
    try:
        frozen_investment.invest(1000, "stocks")
    except AccountFrozenError as e:
        print(f"Investment: {e}")

    # ============================================================
    # [6] Полная информация о счетах
    # ============================================================
    print("\n[6] Полная информация о счетах")
    print("-" * 60)

    for name, account in [("Savings", savings),
                          ("Premium", premium),
                          ("Investment", investment)]:
        print(f"\n{name}:")
        for key, value in account.get_account_info().items():
            print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)
