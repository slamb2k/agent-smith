"""Tests for merchant normalization utilities."""

import pytest
from scripts.utils.merchant_normalizer import normalize_merchant, find_similar_merchants


def test_normalize_merchant_handles_uppercase_and_whitespace():
    """Test normalize_merchant converts to uppercase and strips whitespace."""
    assert normalize_merchant("  woolworths  ") == "WOOLWORTHS"
    assert normalize_merchant("coles") == "COLES"
    assert normalize_merchant("  Aldi Stores  ") == "ALDI STORES"


def test_normalize_merchant_removes_location_codes():
    """Test normalize_merchant removes location codes from payee names."""
    assert normalize_merchant("WOOLWORTHS 1234") == "WOOLWORTHS"
    assert normalize_merchant("COLES 5678") == "COLES"
    assert normalize_merchant("7-ELEVEN 9012") == "7 ELEVEN"


def test_normalize_merchant_removes_common_suffixes():
    """Test normalize_merchant removes common merchant suffixes."""
    assert normalize_merchant("WOOLWORTHS PTY LTD") == "WOOLWORTHS"
    assert normalize_merchant("COLES SUPERMARKETS") == "COLES"
    assert normalize_merchant("ALDI STORES AU") == "ALDI STORES"
    assert normalize_merchant("ACME LIMITED") == "ACME"


def test_normalize_merchant_removes_special_characters():
    """Test normalize_merchant removes or normalizes special characters."""
    assert normalize_merchant("WOOLWORTHS*EPPING") == "WOOLWORTHS EPPING"
    assert normalize_merchant("ACME-COMPANY") == "ACME COMPANY"
    assert normalize_merchant("7/ELEVEN") == "7 ELEVEN"


def test_find_similar_merchants_returns_matches_above_threshold():
    """Test find_similar_merchants returns merchants above similarity threshold."""
    merchants = [
        "WOOLWORTHS",
        "WOOLWORTHS EPPING",
        "COLES",
        "ALDI",
        "WOOLWORTH",
    ]

    # Should find WOOLWORTHS variations with high threshold
    results = find_similar_merchants("WOOLWORTHS", merchants, threshold=0.85)
    assert "WOOLWORTHS" in results  # Exact match
    assert "WOOLWORTH" in results  # Very close match
    assert "COLES" not in results
    assert "ALDI" not in results

    # With lower threshold, should also find partial matches
    results_lower = find_similar_merchants("WOOLWORTHS", merchants, threshold=0.6)
    assert "WOOLWORTHS EPPING" in results_lower


def test_find_similar_merchants_sorted_by_similarity():
    """Test find_similar_merchants returns results sorted by similarity (highest first)."""
    merchants = [
        "COLES",
        "WOOLWORTHS",
        "WOOLWORTHS EPPING",
        "WOOLWORTH",
    ]

    results = find_similar_merchants("WOOLWORTHS", merchants, threshold=0.6)

    # Should have matches
    assert len(results) > 0
    # Exact match should be first (highest similarity = 1.0)
    assert results[0] == "WOOLWORTHS"
    # More similar should come before less similar
    # WOOLWORTH has higher similarity than WOOLWORTHS EPPING
    assert results.index("WOOLWORTH") < results.index("WOOLWORTHS EPPING")
