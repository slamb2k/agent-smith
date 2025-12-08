"""Pydantic models for PocketSmith API entities.

This module provides strongly-typed models with runtime validation for all
PocketSmith API responses. Models include computed fields for common
calculations like GST and absolute amounts.

Key Features:
- Runtime validation of API responses
- Computed fields (gst_amount, absolute_amount, is_expense, is_income)
- Frozen models for cache key hashability
- Aliases for snake_case ↔ camelCase mapping
- Extra fields ignored gracefully (handles API schema drift)
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Any, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)


# =============================================================================
# Enums
# =============================================================================


class TransactionType(str, Enum):
    """Transaction type: debit (expense) or credit (income)."""

    DEBIT = "debit"
    CREDIT = "credit"


class TransactionStatus(str, Enum):
    """Transaction processing status."""

    PENDING = "pending"
    POSTED = "posted"


class AccountType(str, Enum):
    """Account type classification."""

    BANK = "bank"
    CREDITS = "credits"
    CASH = "cash"
    STOCKS = "stocks"
    MORTGAGE = "mortgage"
    LOANS = "loans"
    VEHICLE = "vehicle"
    PROPERTY = "property"
    INSURANCE = "insurance"
    OTHER_ASSET = "other_asset"
    OTHER_LIABILITY = "other_liability"


class RefundBehaviour(str, Enum):
    """Category refund behaviour for budgeting."""

    DEBITS_ARE_DEDUCTIONS = "debits_are_deductions"
    CREDITS_ARE_REFUNDS = "credits_are_refunds"


# =============================================================================
# Base Configuration
# =============================================================================


class PocketSmithModel(BaseModel):
    """Base model for all PocketSmith entities.

    Configuration:
    - extra="ignore": Gracefully handles new API fields
    - populate_by_name=True: Allows both snake_case and original names
    - frozen=True: Immutable for use as cache keys (hashable)
    - str_strip_whitespace=True: Clean string inputs
    """

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        str_strip_whitespace=True,
        # Note: frozen=True is set on individual models where needed
        # Some models need to be mutable for local state
    )


class FrozenPocketSmithModel(PocketSmithModel):
    """Immutable base model for cache-key usage."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        str_strip_whitespace=True,
        frozen=True,
    )


# =============================================================================
# Category Models
# =============================================================================


class Category(FrozenPocketSmithModel):
    """PocketSmith category with optional hierarchy.

    Categories form a tree structure where parent categories contain
    child categories. The API returns children nested in the 'children' array.
    """

    id: int
    title: str
    colour: Optional[str] = Field(default=None, alias="color")
    parent_id: Optional[int] = None
    is_transfer: bool = False
    is_bill: bool = False
    roll_up: bool = False
    refund_behaviour: Optional[RefundBehaviour] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Hierarchy - children are optional and may be empty
    children: tuple["Category", ...] = Field(default_factory=tuple)

    # Computed hierarchy level (set during flattening)
    hierarchy_level: int = 0

    @field_validator("children", mode="before")
    @classmethod
    def convert_children_to_tuple(cls, v: Any) -> tuple["Category", ...]:
        """Convert children list to tuple for immutability."""
        if v is None:
            return ()
        if isinstance(v, (list, tuple)):
            return tuple(
                Category.model_validate(c) if isinstance(c, dict) else c for c in v
            )
        return ()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def full_path(self) -> str:
        """Get category title (without parent path - parent info not available)."""
        return self.title

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_children(self) -> bool:
        """Check if category has child categories."""
        return len(self.children) > 0


# =============================================================================
# Transaction Account Models
# =============================================================================


class Institution(FrozenPocketSmithModel):
    """Financial institution (bank) details."""

    id: int
    title: str
    currency_code: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TransactionAccount(FrozenPocketSmithModel):
    """Transaction account where transactions are recorded.

    This is distinct from Account - a single Account may have multiple
    TransactionAccounts (e.g., different currencies).
    """

    id: int
    name: str
    number: Optional[str] = None
    current_balance: Decimal = Decimal("0")
    current_balance_date: Optional[date] = None
    current_balance_in_base_currency: Optional[Decimal] = None
    current_balance_exchange_rate: Optional[Decimal] = None
    safe_balance: Optional[Decimal] = None
    safe_balance_in_base_currency: Optional[Decimal] = None
    starting_balance: Decimal = Decimal("0")
    starting_balance_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    institution: Optional[Institution] = None
    currency_code: Optional[str] = None
    type: Optional[AccountType] = None

    @field_validator(
        "current_balance",
        "current_balance_in_base_currency",
        "current_balance_exchange_rate",
        "safe_balance",
        "safe_balance_in_base_currency",
        "starting_balance",
        mode="before",
    )
    @classmethod
    def convert_to_decimal(cls, v: Any) -> Optional[Decimal]:
        """Convert numeric values to Decimal for precision."""
        if v is None:
            return None
        return Decimal(str(v))


# =============================================================================
# Account Models
# =============================================================================


class Account(FrozenPocketSmithModel):
    """Top-level account container.

    An Account groups one or more TransactionAccounts and may have
    associated scenarios for forecasting.
    """

    id: int
    title: str
    currency_code: str
    type: AccountType
    is_net_worth: bool = True
    current_balance: Decimal = Decimal("0")
    current_balance_date: Optional[date] = None
    current_balance_in_base_currency: Optional[Decimal] = None
    current_balance_exchange_rate: Optional[Decimal] = None
    safe_balance: Optional[Decimal] = None
    safe_balance_in_base_currency: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Related entities
    primary_transaction_account: Optional[TransactionAccount] = None
    transaction_accounts: tuple[TransactionAccount, ...] = Field(default_factory=tuple)

    @field_validator("transaction_accounts", mode="before")
    @classmethod
    def convert_accounts_to_tuple(
        cls, v: Any
    ) -> tuple[TransactionAccount, ...]:
        """Convert transaction accounts list to tuple."""
        if v is None:
            return ()
        if isinstance(v, (list, tuple)):
            return tuple(
                TransactionAccount.model_validate(a) if isinstance(a, dict) else a
                for a in v
            )
        return ()

    @field_validator(
        "current_balance",
        "current_balance_in_base_currency",
        "current_balance_exchange_rate",
        "safe_balance",
        "safe_balance_in_base_currency",
        mode="before",
    )
    @classmethod
    def convert_to_decimal(cls, v: Any) -> Optional[Decimal]:
        """Convert numeric values to Decimal."""
        if v is None:
            return None
        return Decimal(str(v))


# =============================================================================
# Transaction Models
# =============================================================================


class Transaction(FrozenPocketSmithModel):
    """PocketSmith transaction with computed tax fields.

    Transactions are the core entity - representing actual financial movements.
    This model includes computed fields for Australian tax calculations.
    """

    id: int
    payee: Optional[str] = None
    original_payee: Optional[str] = None
    amount: Decimal
    amount_in_base_currency: Optional[Decimal] = None
    date: date
    type: TransactionType
    memo: Optional[str] = None
    note: Optional[str] = None
    cheque_number: Optional[str] = None
    is_transfer: bool = False
    closing_balance: Optional[Decimal] = None
    status: TransactionStatus = TransactionStatus.POSTED
    needs_review: bool = False
    upload_source: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Related entities (embedded)
    category: Optional[Category] = None
    transaction_account: Optional[TransactionAccount] = None

    # Labels stored as tuple for immutability
    labels: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("labels", mode="before")
    @classmethod
    def convert_labels(cls, v: Any) -> tuple[str, ...]:
        """Convert labels from various formats to tuple.

        PocketSmith API returns labels as comma-separated string or list.
        """
        if v is None:
            return ()
        if isinstance(v, str):
            # Handle comma-separated string
            if not v.strip():
                return ()
            return tuple(label.strip() for label in v.split(",") if label.strip())
        if isinstance(v, (list, tuple)):
            return tuple(str(label).strip() for label in v if label)
        return ()

    @field_validator(
        "amount",
        "amount_in_base_currency",
        "closing_balance",
        mode="before",
    )
    @classmethod
    def convert_to_decimal(cls, v: Any) -> Optional[Decimal]:
        """Convert numeric values to Decimal for precision."""
        if v is None:
            return None
        return Decimal(str(v))

    # -------------------------------------------------------------------------
    # Computed Fields
    # -------------------------------------------------------------------------

    @computed_field  # type: ignore[prop-decorator]
    @property
    def absolute_amount(self) -> Decimal:
        """Get absolute (positive) amount for display."""
        return abs(self.amount)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_expense(self) -> bool:
        """Check if transaction is an expense (debit)."""
        return self.type == TransactionType.DEBIT

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_income(self) -> bool:
        """Check if transaction is income (credit)."""
        return self.type == TransactionType.CREDIT

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_categorized(self) -> bool:
        """Check if transaction has a category assigned."""
        return self.category is not None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def category_title(self) -> Optional[str]:
        """Get category title if assigned."""
        return self.category.title if self.category else None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def category_id(self) -> Optional[int]:
        """Get category ID if assigned."""
        return self.category.id if self.category else None

    # -------------------------------------------------------------------------
    # Australian Tax Computed Fields
    # -------------------------------------------------------------------------

    @computed_field  # type: ignore[prop-decorator]
    @property
    def gst_amount(self) -> Decimal:
        """Calculate GST component (Australian 10% GST).

        GST is calculated as amount/11 for GST-inclusive amounts.
        Only applicable to expenses (debits).
        """
        if self.type != TransactionType.DEBIT:
            return Decimal("0")
        return (abs(self.amount) / Decimal("11")).quantize(Decimal("0.01"))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def gst_exclusive_amount(self) -> Decimal:
        """Calculate GST-exclusive amount (amount - GST)."""
        if self.type != TransactionType.DEBIT:
            return abs(self.amount)
        return abs(self.amount) - self.gst_amount

    # -------------------------------------------------------------------------
    # Label Helpers
    # -------------------------------------------------------------------------

    def has_label(self, label: str) -> bool:
        """Check if transaction has a specific label (case-insensitive)."""
        label_lower = label.lower()
        return any(l.lower() == label_lower for l in self.labels)

    def has_review_label(self) -> bool:
        """Check if transaction has any review flag label."""
        return any("review:" in label.lower() for label in self.labels)


# =============================================================================
# User Models
# =============================================================================


class User(FrozenPocketSmithModel):
    """PocketSmith user account."""

    id: int
    login: str
    name: Optional[str] = None
    email: str
    avatar_url: Optional[str] = None
    beta_user: bool = False
    time_zone: str = "UTC"
    week_start_day: int = Field(default=0, ge=0, le=6)
    is_reviewing_transactions: bool = False
    base_currency_code: str = "USD"
    always_show_base_currency: bool = False
    using_multiple_currencies: bool = False
    available_accounts: int = 0
    available_budgets: int = 0
    forecast_last_updated_at: Optional[datetime] = None
    forecast_last_accessed_at: Optional[datetime] = None
    forecast_start_date: Optional[date] = None
    forecast_end_date: Optional[date] = None
    forecast_defer_recalculate: bool = False
    forecast_needs_recalculate: bool = False
    last_logged_in_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =============================================================================
# Label Models
# =============================================================================


class LabelNamespace(str, Enum):
    """Standard label namespaces for organization."""

    SHARING = "sharing"
    FAMILY = "family"
    BUSINESS = "business"
    TAX = "tax"
    TEMPORAL = "temporal"
    REVIEW = "review"


class Label(FrozenPocketSmithModel):
    """Structured label with namespace and metadata."""

    id: Optional[int] = None
    name: str
    namespace: Optional[LabelNamespace] = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def normalized_name(self) -> str:
        """Get normalized label name (lowercase, hyphenated)."""
        return self.name.lower().replace(" ", "-").replace("_", "-")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_review_label(self) -> bool:
        """Check if this is a system review label."""
        return self.namespace == LabelNamespace.REVIEW or "review:" in self.name.lower()


# =============================================================================
# Category Rule Models
# =============================================================================


class CategoryRule(FrozenPocketSmithModel):
    """PocketSmith platform category rule."""

    id: int
    payee_matches: str
    category: Optional[Category] = None
    apply_to_all: bool = True
    apply_to_uncategorised: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =============================================================================
# Request/Update Models (Mutable)
# =============================================================================


class TransactionUpdate(PocketSmithModel):
    """Mutable model for transaction update requests.

    Use this when updating transactions via the API.
    """

    category_id: Optional[int] = None
    note: Optional[str] = None
    labels: Optional[list[str]] = None
    needs_review: Optional[bool] = None
    payee: Optional[str] = None
    memo: Optional[str] = None

    def to_api_dict(self) -> dict[str, Any]:
        """Convert to API-compatible dictionary.

        Handles label serialization (API expects comma-separated string).
        """
        data: dict[str, Any] = {}
        if self.category_id is not None:
            data["category_id"] = self.category_id
        if self.note is not None:
            data["note"] = self.note
        if self.labels is not None:
            data["labels"] = ",".join(self.labels)
        if self.needs_review is not None:
            data["needs_review"] = self.needs_review
        if self.payee is not None:
            data["payee"] = self.payee
        if self.memo is not None:
            data["memo"] = self.memo
        return data


class TransactionListParams(PocketSmithModel):
    """Parameters for listing transactions with validation."""

    start_date: Optional[date] = None
    end_date: Optional[date] = None
    uncategorised: Optional[bool] = None
    needs_review: Optional[bool] = None
    account_id: Optional[int] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=100, ge=1, le=100)

    @model_validator(mode="after")
    def validate_date_range(self) -> "TransactionListParams":
        """Ensure start_date <= end_date."""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("start_date must be before or equal to end_date")
        return self

    def to_api_params(self) -> dict[str, Any]:
        """Convert to API query parameters."""
        params: dict[str, Any] = {
            "page": self.page,
            "per_page": self.per_page,
        }
        if self.start_date:
            params["start_date"] = self.start_date.isoformat()
        if self.end_date:
            params["end_date"] = self.end_date.isoformat()
        if self.uncategorised is not None:
            params["uncategorised"] = 1 if self.uncategorised else 0
        if self.needs_review is not None:
            params["needs_review"] = self.needs_review
        if self.account_id:
            params["account_id"] = self.account_id
        if self.search:
            params["search"] = self.search
        return params


# =============================================================================
# Type Aliases for Collections
# =============================================================================

TransactionList = Annotated[list[Transaction], Field(description="List of transactions")]
CategoryList = Annotated[list[Category], Field(description="List of categories")]
AccountList = Annotated[list[Account], Field(description="List of accounts")]
TransactionAccountList = Annotated[
    list[TransactionAccount], Field(description="List of transaction accounts")
]
