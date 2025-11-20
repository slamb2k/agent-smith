"""Tests for merchant normalization."""

import pytest
from scripts.utils.merchant_normalizer import MerchantNormalizer


def test_normalize_removes_location_codes():
    """Test normalizer removes location codes from payee names."""
    normalizer = MerchantNormalizer()

    assert normalizer.normalize("WOOLWORTHS 1234") == "WOOLWORTHS"
    assert normalizer.normalize("COLES 5678") == "COLES"
    assert normalizer.normalize("7-ELEVEN 9012") == "7-ELEVEN"


def test_normalize_removes_common_suffixes():
    """Test normalizer removes common merchant suffixes."""
    normalizer = MerchantNormalizer()

    assert normalizer.normalize("WOOLWORTHS PTY LTD") == "WOOLWORTHS"
    assert normalizer.normalize("COLES SUPERMARKETS") == "COLES"
    assert normalizer.normalize("ALDI STORES AU") == "ALDI STORES"


def test_normalize_handles_transaction_codes():
    """Test normalizer removes transaction codes."""
    normalizer = MerchantNormalizer()

    assert normalizer.normalize("WOOLWORTHS EPPING NSWxxx123") == "WOOLWORTHS EPPING"
    assert normalizer.normalize("Direct Debit 123456") == "DIRECT DEBIT"


def test_canonical_name_mapping():
    """Test canonical name mapping from variations."""
    normalizer = MerchantNormalizer()

    # Add mapping
    normalizer.add_mapping("WOOLWORTHS", ["WOOLWORTHS", "WOOLIES", "WW"])

    assert normalizer.get_canonical_name("WOOLWORTHS 1234") == "WOOLWORTHS"
    assert normalizer.get_canonical_name("WOOLIES EPPING") == "WOOLWORTHS"
    assert normalizer.get_canonical_name("WW SUPERMARKET") == "WOOLWORTHS"


def test_learn_from_transaction_variations():
    """Test learning merchant variations from transaction history."""
    normalizer = MerchantNormalizer()

    transactions = [
        {"payee": "WOOLWORTHS 1234"},
        {"payee": "WOOLWORTHS 5678"},
        {"payee": "WOOLWORTHS EPPING"},
        {"payee": "COLES 9012"},
        {"payee": "COLES SUPERMARKET"},
    ]

    normalizer.learn_from_transactions(transactions)

    # Should group WOOLWORTHS variations
    assert normalizer.get_canonical_name("WOOLWORTHS 9999") == "WOOLWORTHS"
    assert normalizer.get_canonical_name("COLES 1111") == "COLES"
