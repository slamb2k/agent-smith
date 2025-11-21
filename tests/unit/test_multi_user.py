import pytest
from datetime import datetime
from scripts.features.multi_user import SharedExpense, Settlement, SharedExpenseTracker


def test_shared_expense_creation():
    """Test creating a shared expense."""
    expense = SharedExpense(
        transaction_id=12345,
        amount=120.00,
        description="Groceries",
        paid_by="alice",
        date=datetime(2025, 11, 15),
        splits={"alice": 60.00, "bob": 60.00},
    )

    assert expense.transaction_id == 12345
    assert expense.amount == 120.00
    assert expense.paid_by == "alice"
    assert expense.splits["alice"] == 60.00
    assert expense.splits["bob"] == 60.00


def test_shared_expense_calculate_owes():
    """Test calculating who owes whom."""
    expense = SharedExpense(
        transaction_id=12345,
        amount=120.00,
        description="Groceries",
        paid_by="alice",
        date=datetime(2025, 11, 15),
        splits={"alice": 60.00, "bob": 60.00},
    )

    # Bob owes Alice $60 (Alice paid $120, owes $60)
    owes = expense.calculate_owes()
    assert owes["bob"] == 60.00
    assert "alice" not in owes  # Alice doesn't owe herself


def test_shared_expense_custom_splits():
    """Test expense with custom split ratios."""
    expense = SharedExpense(
        transaction_id=12346,
        amount=150.00,
        description="Dinner",
        paid_by="charlie",
        date=datetime(2025, 11, 16),
        splits={"alice": 50.00, "bob": 50.00, "charlie": 50.00},
    )

    owes = expense.calculate_owes()
    assert owes["alice"] == 50.00
    assert owes["bob"] == 50.00
    assert "charlie" not in owes


def test_settlement_creation():
    """Test creating a settlement record."""
    settlement = Settlement(
        from_user="bob",
        to_user="alice",
        amount=150.00,
        date=datetime(2025, 11, 20),
        transaction_ids=[12345, 12346],
    )

    assert settlement.from_user == "bob"
    assert settlement.to_user == "alice"
    assert settlement.amount == 150.00
    assert len(settlement.transaction_ids) == 2


def test_shared_expense_tracker_initialization():
    """Test creating shared expense tracker."""
    tracker = SharedExpenseTracker(users=["alice", "bob", "charlie"])
    assert len(tracker.users) == 3
    assert len(tracker.expenses) == 0


def test_shared_expense_tracker_add_expense():
    """Test adding a shared expense."""
    tracker = SharedExpenseTracker(users=["alice", "bob"])

    expense = tracker.add_expense(
        transaction_id=12345,
        amount=100.00,
        description="Dinner",
        paid_by="alice",
        date=datetime(2025, 11, 15),
        split_equally=True,
    )

    assert expense.transaction_id == 12345
    assert expense.splits["alice"] == 50.00
    assert expense.splits["bob"] == 50.00
    assert len(tracker.expenses) == 1


def test_shared_expense_tracker_custom_split():
    """Test adding expense with custom split ratios."""
    tracker = SharedExpenseTracker(users=["alice", "bob", "charlie"])

    expense = tracker.add_expense(
        transaction_id=12346,
        amount=120.00,
        description="Groceries",
        paid_by="bob",
        date=datetime(2025, 11, 16),
        split_ratios={"alice": 0.5, "bob": 0.25, "charlie": 0.25},
    )

    assert expense.splits["alice"] == 60.00
    assert expense.splits["bob"] == 30.00
    assert expense.splits["charlie"] == 30.00


def test_shared_expense_tracker_calculate_balances():
    """Test calculating who owes whom across all expenses."""
    tracker = SharedExpenseTracker(users=["alice", "bob"])

    # Alice pays $100, split equally
    tracker.add_expense(
        transaction_id=1,
        amount=100.00,
        description="Dinner",
        paid_by="alice",
        date=datetime(2025, 11, 15),
        split_equally=True,
    )

    # Bob pays $60, split equally
    tracker.add_expense(
        transaction_id=2,
        amount=60.00,
        description="Coffee",
        paid_by="bob",
        date=datetime(2025, 11, 16),
        split_equally=True,
    )

    # Alice paid $100, owes $30 = net +$70
    # Bob paid $60, owes $50 = net -$10
    # Result: Bob owes Alice $20
    balances = tracker.calculate_balances()
    assert balances["bob"] == -20.00  # Negative = owes
    assert balances["alice"] == 20.00  # Positive = owed


def test_shared_expense_tracker_generate_settlements():
    """Test generating settlement recommendations."""
    tracker = SharedExpenseTracker(users=["alice", "bob", "charlie"])

    # Alice pays $150
    tracker.add_expense(
        transaction_id=1,
        amount=150.00,
        description="Dinner",
        paid_by="alice",
        date=datetime(2025, 11, 15),
        split_equally=True,
    )

    # Bob pays $90
    tracker.add_expense(
        transaction_id=2,
        amount=90.00,
        description="Drinks",
        paid_by="bob",
        date=datetime(2025, 11, 16),
        split_equally=True,
    )

    # Alice: paid $150, owes $80 = net +$70
    # Bob: paid $90, owes $80 = net +$10
    # Charlie: paid $0, owes $80 = net -$80
    # Charlie owes Alice $70, Charlie owes Bob $10

    settlements = tracker.generate_settlements()
    assert len(settlements) == 2

    # Find Charlie -> Alice settlement
    charlie_to_alice = next(
        s for s in settlements if s.from_user == "charlie" and s.to_user == "alice"
    )
    assert charlie_to_alice.amount == 70.00

    # Find Charlie -> Bob settlement
    charlie_to_bob = next(s for s in settlements if s.from_user == "charlie" and s.to_user == "bob")
    assert charlie_to_bob.amount == 10.00


def test_shared_expense_tracker_rejects_unknown_payer():
    """Test that add_expense rejects unknown payer."""
    tracker = SharedExpenseTracker(users=["alice", "bob"])

    with pytest.raises(ValueError, match="Unknown payer: unknown not in users list"):
        tracker.add_expense(
            transaction_id=1,
            amount=100.00,
            description="Dinner",
            paid_by="unknown",
            date=datetime(2025, 11, 15),
            split_equally=True,
        )


def test_shared_expense_tracker_validates_split_ratios_sum():
    """Test that add_expense validates split_ratios sum to 1.0."""
    tracker = SharedExpenseTracker(users=["alice", "bob"])

    # Test ratios that don't sum to 1.0
    with pytest.raises(ValueError, match="Split ratios must sum to 1.0, got 0.8000"):
        tracker.add_expense(
            transaction_id=1,
            amount=100.00,
            description="Dinner",
            paid_by="alice",
            date=datetime(2025, 11, 15),
            split_ratios={"alice": 0.5, "bob": 0.3},
        )


def test_shared_expense_tracker_validates_split_ratios_users():
    """Test that add_expense validates split_ratios only include known users."""
    tracker = SharedExpenseTracker(users=["alice", "bob"])

    with pytest.raises(ValueError, match="Unknown users in split_ratios: charlie"):
        tracker.add_expense(
            transaction_id=1,
            amount=120.00,
            description="Dinner",
            paid_by="alice",
            date=datetime(2025, 11, 15),
            split_ratios={"alice": 0.5, "bob": 0.25, "charlie": 0.25},
        )
