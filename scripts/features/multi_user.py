"""Multi-user and shared expense tracking."""

from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SharedExpense:
    """Represents a shared expense between users."""

    transaction_id: int
    amount: float
    description: str
    paid_by: str
    date: datetime
    splits: Dict[str, float]
    settled: bool = False

    def calculate_owes(self) -> Dict[str, float]:
        """Calculate who owes whom for this expense.

        Returns:
            Dict mapping user_id to amount they owe the payer
        """
        owes = {}

        for user, owed_amount in self.splits.items():
            if user != self.paid_by:
                owes[user] = owed_amount

        return owes


@dataclass
class Settlement:
    """Represents a settlement payment between users."""

    from_user: str
    to_user: str
    amount: float
    date: datetime
    transaction_ids: List[int]
    notes: Optional[str] = None


class SharedExpenseTracker:
    """Manages shared expenses and settlement calculations."""

    def __init__(self, users: List[str]):
        """Initialize tracker with list of users.

        Args:
            users: List of user IDs participating in shared expenses
        """
        self.users = users
        self.expenses: List[SharedExpense] = []
        self.settlements: List[Settlement] = []

    def add_expense(
        self,
        transaction_id: int,
        amount: float,
        description: str,
        paid_by: str,
        date: datetime,
        split_equally: bool = False,
        split_ratios: Optional[Dict[str, float]] = None,
    ) -> SharedExpense:
        """Add a shared expense.

        Args:
            transaction_id: Transaction ID
            amount: Total amount
            description: Expense description
            paid_by: User who paid
            date: Transaction date
            split_equally: Split equally among all users
            split_ratios: Custom split ratios (must sum to 1.0)

        Returns:
            Created SharedExpense
        """
        if split_equally:
            split_amount = amount / len(self.users)
            splits = {user: split_amount for user in self.users}
        elif split_ratios:
            splits = {user: amount * ratio for user, ratio in split_ratios.items()}
        else:
            raise ValueError("Must specify either split_equally or split_ratios")

        expense = SharedExpense(
            transaction_id=transaction_id,
            amount=amount,
            description=description,
            paid_by=paid_by,
            date=date,
            splits=splits,
        )

        self.expenses.append(expense)
        return expense

    def calculate_balances(self) -> Dict[str, float]:
        """Calculate net balance for each user.

        Returns:
            Dict mapping user_id to balance (positive = owed, negative = owes)
        """
        balances = {user: 0.0 for user in self.users}

        for expense in self.expenses:
            if expense.settled:
                continue

            # Add amount paid
            balances[expense.paid_by] += expense.amount

            # Subtract amount owed
            for user, owed in expense.splits.items():
                balances[user] -= owed

        return balances

    def generate_settlements(self) -> List[Settlement]:
        """Generate settlement recommendations to balance all accounts.

        Returns:
            List of Settlement objects
        """
        balances = self.calculate_balances()
        settlements = []

        # Separate creditors (positive balance) and debtors (negative balance)
        creditors = {u: b for u, b in balances.items() if b > 0.01}
        debtors = {u: -b for u, b in balances.items() if b < -0.01}

        # Match debtors with creditors
        for debtor, debt_amount in debtors.items():
            remaining_debt = debt_amount

            for creditor, credit_amount in list(creditors.items()):
                if remaining_debt <= 0.01:
                    break

                # Settle the smaller of the two amounts
                settlement_amount = min(remaining_debt, credit_amount)

                settlements.append(
                    Settlement(
                        from_user=debtor,
                        to_user=creditor,
                        amount=round(settlement_amount, 2),
                        date=datetime.now(),
                        transaction_ids=[e.transaction_id for e in self.expenses if not e.settled],
                    )
                )

                remaining_debt -= settlement_amount
                creditors[creditor] -= settlement_amount

                if creditors[creditor] <= 0.01:
                    del creditors[creditor]

        return settlements
