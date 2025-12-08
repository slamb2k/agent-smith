"""Core V2: Pydantic-based foundation for Agent Smith.

This module provides strongly-typed, cached access to the PocketSmith API.

Quick Start:
    from scripts.core_v2 import PocketSmithClientV2, Transaction, Category

    client = PocketSmithClientV2()
    user = client.get_user()
    transactions = client.get_all_transactions(user.id, uncategorised=True)

    for txn in transactions:
        print(f"{txn.payee}: ${txn.absolute_amount} (GST: ${txn.gst_amount})")

Models:
    - Transaction: Financial transaction with computed tax fields
    - Category: Hierarchical category with children
    - User: PocketSmith user account
    - Account: Top-level account container
    - TransactionAccount: Account where transactions are recorded

Cache:
    - PocketSmithCache: Multi-tier caching with TTL policies
    - CachePolicy: TTL configurations for different data types
    - CacheKey: Structured cache key generation

Client:
    - PocketSmithClientV2: Type-safe API client with caching
"""

# Models
from .models import (
    # Enums
    AccountType,
    LabelNamespace,
    RefundBehaviour,
    TransactionStatus,
    TransactionType,
    # Core models
    Account,
    Category,
    CategoryRule,
    Institution,
    Label,
    Transaction,
    TransactionAccount,
    User,
    # Request models
    TransactionListParams,
    TransactionUpdate,
    # Type aliases
    AccountList,
    CategoryList,
    TransactionAccountList,
    TransactionList,
)

# Cache
from .cache import (
    CacheEntry,
    CacheKey,
    CachePolicy,
    CacheStats,
    PocketSmithCache,
    cached,
    get_global_cache,
    set_global_cache,
)

# Client
from .client import PocketSmithClientV2

__all__ = [
    # Enums
    "AccountType",
    "LabelNamespace",
    "RefundBehaviour",
    "TransactionStatus",
    "TransactionType",
    # Core models
    "Account",
    "Category",
    "CategoryRule",
    "Institution",
    "Label",
    "Transaction",
    "TransactionAccount",
    "User",
    # Request models
    "TransactionListParams",
    "TransactionUpdate",
    # Type aliases
    "AccountList",
    "CategoryList",
    "TransactionAccountList",
    "TransactionList",
    # Cache
    "CacheEntry",
    "CacheKey",
    "CachePolicy",
    "CacheStats",
    "PocketSmithCache",
    "cached",
    "get_global_cache",
    "set_global_cache",
    # Client
    "PocketSmithClientV2",
]
