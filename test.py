import unittest

from bank_account import BankAccount, InsufficientFundsError, InvalidAmountError


class TestCreation(unittest.TestCase):
    def test_owner_and_number_are_stored(self):
        acc = BankAccount("Иван Петров", "KG001")
        self.assertEqual(acc.owner, "Иван Петров")
        self.assertEqual(acc.account_number, "KG001")

    def test_initial_balance_is_zero(self):
        self.assertEqual(BankAccount("Иван", "KG001").balance, 0)

    def test_empty_owner_rejected(self):
        for bad in ("", "   ", None, 123):
            with self.subTest(owner=bad):
                with self.assertRaises(ValueError):
                    BankAccount(bad, "KG001")

    def test_empty_account_number_rejected(self):
        for bad in ("", "   ", None, 123):
            with self.subTest(number=bad):
                with self.assertRaises(ValueError):
                    BankAccount("Иван", bad)

    def test_balance_is_read_only(self):
        acc = BankAccount("Иван", "KG001")
        with self.assertRaises(AttributeError):
            acc.balance = 1000


class TestDeposit(unittest.TestCase):
    def setUp(self):
        self.acc = BankAccount("Иван", "KG001")

    def test_deposit_increases_balance(self):
        self.acc.deposit(100)
        self.assertEqual(self.acc.balance, 100)

    def test_multiple_deposits_accumulate(self):
        self.acc.deposit(100)
        self.acc.deposit(50)
        self.assertEqual(self.acc.balance, 150)

    def test_deposit_float(self):
        self.acc.deposit(10.5)
        self.assertAlmostEqual(self.acc.balance, 10.5)

    def test_deposit_invalid_amounts(self):
        invalid = [0, -1, -0.01, "100", None, True, [10], float("nan"), float("inf")]
        for amount in invalid:
            with self.subTest(amount=amount):
                with self.assertRaises(InvalidAmountError):
                    self.acc.deposit(amount)
                self.assertEqual(self.acc.balance, 0)


class TestWithdraw(unittest.TestCase):
    def setUp(self):
        self.acc = BankAccount("Иван", "KG001")
        self.acc.deposit(100)

    def test_withdraw_decreases_balance(self):
        self.acc.withdraw(30)
        self.assertEqual(self.acc.balance, 70)

    def test_withdraw_entire_balance(self):
        self.acc.withdraw(100)
        self.assertEqual(self.acc.balance, 0)

    def test_withdraw_more_than_balance_rejected(self):
        with self.assertRaises(InsufficientFundsError):
            self.acc.withdraw(100.01)
        self.assertEqual(self.acc.balance, 100)

    def test_withdraw_from_empty_account_rejected(self):
        empty = BankAccount("Пётр", "KG002")
        with self.assertRaises(InsufficientFundsError):
            empty.withdraw(1)
        self.assertEqual(empty.balance, 0)

    def test_withdraw_invalid_amounts(self):
        for amount in (0, -5, "10", None, False, float("nan")):
            with self.subTest(amount=amount):
                with self.assertRaises(InvalidAmountError):
                    self.acc.withdraw(amount)
                self.assertEqual(self.acc.balance, 100)


class TestTransfer(unittest.TestCase):
    def setUp(self):
        self.sender = BankAccount("Иван", "KG001")
        self.receiver = BankAccount("Пётр", "KG002")
        self.sender.deposit(200)
        self.receiver.deposit(50)

    def test_successful_transfer(self):
        self.sender.transfer(self.receiver, 80)
        self.assertEqual(self.sender.balance, 120)
        self.assertEqual(self.receiver.balance, 130)

    def test_changes_are_equal_in_magnitude(self):
        before_s, before_r = self.sender.balance, self.receiver.balance
        self.sender.transfer(self.receiver, 75)
        self.assertEqual(before_s - self.sender.balance,
                         self.receiver.balance - before_r)

    def test_total_money_is_preserved(self):
        total = self.sender.balance + self.receiver.balance
        self.sender.transfer(self.receiver, 123)
        self.assertEqual(self.sender.balance + self.receiver.balance, total)

    def test_transfer_entire_balance(self):
        self.sender.transfer(self.receiver, 200)
        self.assertTrue(self.sender.is_empty())
        self.assertEqual(self.receiver.balance, 250)

    def test_insufficient_funds_leaves_accounts_unchanged(self):
        with self.assertRaises(InsufficientFundsError):
            self.sender.transfer(self.receiver, 200.01)
        self.assertEqual(self.sender.balance, 200)
        self.assertEqual(self.receiver.balance, 50)

    def test_invalid_amount_leaves_accounts_unchanged(self):
        for amount in (0, -10, "50", None, float("inf")):
            with self.subTest(amount=amount):
                with self.assertRaises(InvalidAmountError):
                    self.sender.transfer(self.receiver, amount)
                self.assertEqual(self.sender.balance, 200)
                self.assertEqual(self.receiver.balance, 50)

    def test_transfer_to_non_account_rejected(self):
        for target in (None, "KG002", 42):
            with self.subTest(target=target):
                with self.assertRaises(TypeError):
                    self.sender.transfer(target, 10)
                self.assertEqual(self.sender.balance, 200)

    def test_transfer_to_self_rejected(self):
        with self.assertRaises(ValueError):
            self.sender.transfer(self.sender, 10)
        self.assertEqual(self.sender.balance, 200)


class TestGetBalance(unittest.TestCase):
    def test_new_account(self):
        self.assertEqual(BankAccount("Иван", "KG001").get_balance(), 0)

    def test_balance_after_series_of_operations(self):
        a = BankAccount("Иван", "KG001")
        b = BankAccount("Пётр", "KG002")
        a.deposit(500)
        a.withdraw(120)
        a.transfer(b, 200)
        b.deposit(30)
        b.withdraw(10)
        self.assertEqual(a.get_balance(), 180)
        self.assertEqual(b.get_balance(), 220)

    def test_get_balance_matches_property(self):
        a = BankAccount("Иван", "KG001")
        a.deposit(77)
        self.assertEqual(a.get_balance(), a.balance)


class TestIsEmpty(unittest.TestCase):
    def test_new_account_is_empty(self):
        self.assertTrue(BankAccount("Иван", "KG001").is_empty())

    def test_not_empty_after_deposit(self):
        a = BankAccount("Иван", "KG001")
        a.deposit(1)
        self.assertFalse(a.is_empty())

    def test_empty_after_full_withdrawal(self):
        a = BankAccount("Иван", "KG001")
        a.deposit(100)
        a.withdraw(100)
        self.assertTrue(a.is_empty())

    def test_failed_withdrawal_does_not_empty_account(self):
        a = BankAccount("Иван", "KG001")
        a.deposit(100)
        with self.assertRaises(InsufficientFundsError):
            a.withdraw(101)
        self.assertFalse(a.is_empty())


if __name__ == "__main__":
    unittest.main()