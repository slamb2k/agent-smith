"""Unit tests for core_v2 Pydantic models."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from scripts.core_v2.models import (
    Account,
    AccountType,
    Category,
    CategoryRule,
    Institution,
    Label,
    LabelNamespace,
    RefundBehaviour,
    Transaction,
    TransactionAccount,
    TransactionListParams,
    TransactionStatus,
    TransactionType,
    TransactionUpdate,
    User,
)


class TestTransactionModel:
    """Tests for Transaction model."""

    def test_basic_transaction(self):
        """Test creating a basic transaction."""
        txn = Transaction(
            id=123,
            payee="Coffee Shop",
            amount=Decimal("-4.50"),
            date=date(2024, 1, 15),
            type=TransactionType.DEBIT,
        )

        assert txn.id == 123
        assert txn.payee == "Coffee Shop"
        assert txn.amount == Decimal("-4.50")
        assert txn.date == date(2024, 1, 15)
        assert txn.type == TransactionType.DEBIT

    def test_computed_absolute_amount(self):
        """Test absolute_amount computed field."""
        txn = Transaction(
            id=1,
            amount=Decimal("-100.00"),
            date=date(2024, 1, 1),
            type=TransactionType.DEBIT,
        )

        assert txn.absolute_amount == Decimal("100.00")

    def test_computed_is_expense(self):
        """Test is_expense computed field."""
        debit = Transaction(
            id=1,
            amount=Decimal("-50"),
            date=date(2024, 1, 1),
            type=TransactionType.DEBIT,
        )
        credit = Transaction(
            id=2,
            amount=Decimal("100"),
            date=date(2024, 1, 1),
            type=TransactionType.CREDIT,
        )

        assert debit.is_expense is True
        assert debit.is_income is False
        assert credit.is_expense is False
        assert credit.is_income is True

    def test_computed_gst_amount(self):
        """Test GST calculation (Australian 10% GST)."""
        txn = Transaction(
            id=1,
            amount=Decimal("-110.00"),
            date=date(2024, 1, 1),
            type=TransactionType.DEBIT,
        )

        # GST = 110 / 11 = 10
        assert txn.gst_amount == Decimal("10.00")
        # GST exclusive = 110 - 10 = 100
        assert txn.gst_exclusive_amount == Decimal("100.00")

    def test_gst_not_calculated_for_income(self):
        """Test that GST is not calculated for income."""
        txn = Transaction(
            id=1,
            amount=Decimal("110.00"),
            date=date(2024, 1, 1),
            type=TransactionType.CREDIT,
        )

        assert txn.gst_amount == Decimal("0")
        assert txn.gst_exclusive_amount == Decimal("110.00")

    def test_labels_from_string(self):
        """Test labels parsing from comma-separated string."""
        txn = Transaction(
            id=1,
            amount=Decimal("-10"),
            date=date(2024, 1, 1),
            type=TransactionType.DEBIT,
            labels="Tax Deductible, Business, Review: Needs Check",
        )

        assert len(txn.labels) == 3
        assert "Tax Deductible" in txn.labels
        assert "Business" in txn.labels
        assert "Review: Needs Check" in txn.labels

    def test_labels_from_list(self):
        """Test labels parsing from list."""
        txn = Transaction(
            id=1,
            amount=Decimal("-10"),
            date=date(2024, 1, 1),
            type=TransactionType.DEBIT,
            labels=["Tax", "Business"],
        )

        assert txn.labels == ("Tax", "Business")

    def test_has_label(self):
        """Test has_label method (case-insensitive)."""
        txn = Transaction(
            id=1,
            amount=Decimal("-10"),
            date=date(2024, 1, 1),
            type=TransactionType.DEBIT,
            labels=["Tax Deductible", "Business"],
        )

        assert txn.has_label("Tax Deductible") is True
        assert txn.has_label("tax deductible") is True
        assert txn.has_label("BUSINESS") is True
        assert txn.has_label("Personal") is False

    def test_has_review_label(self):
        """Test has_review_label detection."""
        txn_with_review = Transaction(
            id=1,
            amount=Decimal("-10"),
            date=date(2024, 1, 1),
            type=TransactionType.DEBIT,
            labels=["Review: Category Conflict"],
        )
        txn_without_review = Transaction(
            id=2,
            amount=Decimal("-10"),
            date=date(2024, 1, 1),
            type=TransactionType.DEBIT,
            labels=["Business"],
        )

        assert txn_with_review.has_review_label() is True
        assert txn_without_review.has_review_label() is False

    def test_category_computed_fields(self):
        """Test category-related computed fields."""
        category = Category(id=10, title="Groceries")
        txn = Transaction(
            id=1,
            amount=Decimal("-50"),
            date=date(2024, 1, 1),
            type=TransactionType.DEBIT,
            category=category,
        )

        assert txn.is_categorized is True
        assert txn.category_title == "Groceries"
        assert txn.category_id == 10

    def test_uncategorized_transaction(self):
        """Test uncategorized transaction computed fields."""
        txn = Transaction(
            id=1,
            amount=Decimal("-50"),
            date=date(2024, 1, 1),
            type=TransactionType.DEBIT,
        )

        assert txn.is_categorized is False
        assert txn.category_title is None
        assert txn.category_id is None

    def test_amount_conversion_from_float(self):
        """Test automatic conversion of float to Decimal."""
        txn = Transaction(
            id=1,
            amount="-99.99",  # String should be converted
            date=date(2024, 1, 1),
            type=TransactionType.DEBIT,
        )

        assert isinstance(txn.amount, Decimal)
        assert txn.amount == Decimal("-99.99")

    def test_transaction_is_frozen(self):
        """Test that Transaction is immutable (frozen)."""
        txn = Transaction(
            id=1,
            amount=Decimal("-10"),
            date=date(2024, 1, 1),
            type=TransactionType.DEBIT,
        )

        with pytest.raises(Exception):  # ValidationError or AttributeError
            txn.amount = Decimal("-20")


class TestCategoryModel:
    """Tests for Category model."""

    def test_basic_category(self):
        """Test creating a basic category."""
        cat = Category(
            id=1,
            title="Food & Dining",
            colour="#FF5733",
        )

        assert cat.id == 1
        assert cat.title == "Food & Dining"
        assert cat.colour == "#FF5733"

    def test_category_with_children(self):
        """Test category with nested children."""
        cat = Category(
            id=1,
            title="Food & Dining",
            children=[
                {"id": 2, "title": "Groceries"},
                {"id": 3, "title": "Restaurants"},
            ],
        )

        assert cat.has_children is True
        assert len(cat.children) == 2
        assert cat.children[0].title == "Groceries"
        assert cat.children[1].title == "Restaurants"

    def test_category_without_children(self):
        """Test category without children."""
        cat = Category(id=1, title="Utilities")

        assert cat.has_children is False
        assert cat.children == ()

    def test_colour_alias(self):
        """Test colour/color alias."""
        cat = Category(id=1, title="Test", color="#123456")
        assert cat.colour == "#123456"

    def test_refund_behaviour_enum(self):
        """Test refund behaviour parsing."""
        cat = Category(
            id=1,
            title="Test",
            refund_behaviour="debits_are_deductions",
        )

        assert cat.refund_behaviour == RefundBehaviour.DEBITS_ARE_DEDUCTIONS


class TestUserModel:
    """Tests for User model."""

    def test_basic_user(self):
        """Test creating a basic user."""
        user = User(
            id=12345,
            login="testuser",
            email="test@example.com",
            base_currency_code="AUD",
        )

        assert user.id == 12345
        assert user.login == "testuser"
        assert user.email == "test@example.com"
        assert user.base_currency_code == "AUD"

    def test_week_start_day_validation(self):
        """Test week_start_day range validation."""
        user = User(
            id=1,
            login="test",
            email="t@t.com",
            week_start_day=0,  # Sunday
        )
        assert user.week_start_day == 0

        with pytest.raises(Exception):
            User(
                id=1,
                login="test",
                email="t@t.com",
                week_start_day=7,  # Invalid
            )


class TestAccountModel:
    """Tests for Account model."""

    def test_basic_account(self):
        """Test creating a basic account."""
        account = Account(
            id=1,
            title="Savings Account",
            currency_code="AUD",
            type=AccountType.BANK,
            current_balance="1000.50",
        )

        assert account.id == 1
        assert account.title == "Savings Account"
        assert account.type == AccountType.BANK
        assert account.current_balance == Decimal("1000.50")


class TestTransactionAccountModel:
    """Tests for TransactionAccount model."""

    def test_basic_transaction_account(self):
        """Test creating a transaction account."""
        ta = TransactionAccount(
            id=1,
            name="Checking Account",
            number="1234-5678",
            current_balance="500.00",
            currency_code="AUD",
        )

        assert ta.id == 1
        assert ta.name == "Checking Account"
        assert ta.current_balance == Decimal("500.00")


class TestTransactionListParams:
    """Tests for TransactionListParams validation."""

    def test_valid_date_range(self):
        """Test valid date range."""
        params = TransactionListParams(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )

        assert params.start_date == date(2024, 1, 1)
        assert params.end_date == date(2024, 12, 31)

    def test_invalid_date_range(self):
        """Test that start_date > end_date raises error."""
        with pytest.raises(ValueError, match="start_date must be before"):
            TransactionListParams(
                start_date=date(2024, 12, 31),
                end_date=date(2024, 1, 1),
            )

    def test_to_api_params(self):
        """Test conversion to API parameters."""
        params = TransactionListParams(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            uncategorised=True,
            page=2,
            per_page=50,
        )

        api_params = params.to_api_params()

        assert api_params["start_date"] == "2024-01-01"
        assert api_params["end_date"] == "2024-01-31"
        assert api_params["uncategorised"] == 1
        assert api_params["page"] == 2
        assert api_params["per_page"] == 50

    def test_per_page_validation(self):
        """Test per_page max validation."""
        with pytest.raises(Exception):
            TransactionListParams(per_page=200)  # Max is 100


class TestTransactionUpdate:
    """Tests for TransactionUpdate model."""

    def test_to_api_dict(self):
        """Test conversion to API dictionary."""
        update = TransactionUpdate(
            category_id=123,
            labels=["Tax", "Business"],
            note="Test note",
        )

        api_dict = update.to_api_dict()

        assert api_dict["category_id"] == 123
        assert api_dict["labels"] == "Tax,Business"
        assert api_dict["note"] == "Test note"

    def test_to_api_dict_empty_labels(self):
        """Test that None values are excluded."""
        update = TransactionUpdate(category_id=123)

        api_dict = update.to_api_dict()

        assert api_dict == {"category_id": 123}
        assert "labels" not in api_dict
        assert "note" not in api_dict


class TestLabelModel:
    """Tests for Label model."""

    def test_normalized_name(self):
        """Test label name normalization."""
        label = Label(name="Tax Deductible")

        assert label.normalized_name == "tax-deductible"

    def test_is_review_label(self):
        """Test review label detection."""
        review_label = Label(name="Review: Category Conflict")
        normal_label = Label(name="Business")
        namespace_review = Label(name="Test", namespace=LabelNamespace.REVIEW)

        assert review_label.is_review_label is True
        assert normal_label.is_review_label is False
        assert namespace_review.is_review_label is True


class TestModelValidation:
    """Tests for model validation behavior."""

    def test_extra_fields_ignored(self):
        """Test that extra API fields are ignored gracefully."""
        data = {
            "id": 1,
            "title": "Test",
            "unknown_field": "should be ignored",
            "another_unknown": 123,
        }

        cat = Category.model_validate(data)

        assert cat.id == 1
        assert cat.title == "Test"
        assert not hasattr(cat, "unknown_field")

    def test_from_api_response(self):
        """Test creating model from typical API response."""
        api_response = {
            "id": 12345,
            "payee": "WOOLWORTHS METRO",
            "original_payee": "WOOLWORTHS METRO 1234 SYDNEY",
            "amount": -45.67,
            "amount_in_base_currency": -45.67,
            "date": "2024-11-15",
            "type": "debit",
            "is_transfer": False,
            "memo": None,
            "note": "Weekly groceries",
            "labels": "Groceries,Weekly",
            "status": "posted",
            "needs_review": False,
            "category": {
                "id": 100,
                "title": "Groceries",
                "colour": "#4CAF50",
            },
            "transaction_account": {
                "id": 50,
                "name": "Everyday Account",
                "current_balance": 1234.56,
            },
            "created_at": "2024-11-15T10:30:00Z",
            "updated_at": "2024-11-15T10:30:00Z",
        }

        txn = Transaction.model_validate(api_response)

        assert txn.id == 12345
        assert txn.payee == "WOOLWORTHS METRO"
        assert txn.amount == Decimal("-45.67")
        assert txn.date == date(2024, 11, 15)
        assert txn.type == TransactionType.DEBIT
        assert txn.labels == ("Groceries", "Weekly")
        assert txn.category is not None
        assert txn.category.title == "Groceries"
        assert txn.transaction_account is not None
        assert txn.transaction_account.name == "Everyday Account"

        # Test computed fields
        assert txn.is_expense is True
        assert txn.is_categorized is True
        assert txn.absolute_amount == Decimal("45.67")
        assert txn.gst_amount == Decimal("4.15")  # 45.67 / 11
