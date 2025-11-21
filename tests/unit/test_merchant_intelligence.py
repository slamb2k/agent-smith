import pytest
from scripts.features.merchant_intelligence import MerchantMatcher, MerchantGroup


def test_merchant_matcher_initialization():
    """Test creating merchant matcher."""
    matcher = MerchantMatcher()
    assert matcher is not None
    assert len(matcher.canonical_names) == 0


def test_merchant_matcher_normalize_payee():
    """Test normalizing payee names."""
    matcher = MerchantMatcher()

    # Remove common suffixes
    assert matcher.normalize_payee("WOOLWORTHS PTY LTD") == "woolworths"
    assert matcher.normalize_payee("Coles Pty Ltd") == "coles"

    # Remove transaction IDs
    assert matcher.normalize_payee("UBER *TRIP AB123CD") == "uber trip"
    assert matcher.normalize_payee("SQ *COFFEE SHOP 5678") == "sq coffee shop"

    # Remove extra whitespace
    assert matcher.normalize_payee("  MULTIPLE   SPACES  ") == "multiple spaces"

    # Lowercase
    assert matcher.normalize_payee("MiXeD CaSe") == "mixed case"


def test_merchant_matcher_calculate_similarity():
    """Test calculating similarity between payee names."""
    matcher = MerchantMatcher()

    # Identical
    assert matcher.calculate_similarity("woolworths", "woolworths") == 1.0

    # Very similar
    sim = matcher.calculate_similarity("woolworths", "woolworth")
    assert sim > 0.9

    # Somewhat similar
    sim = matcher.calculate_similarity("woolworths", "woollies")
    assert 0.5 < sim < 0.9

    # Different
    sim = matcher.calculate_similarity("woolworths", "coles")
    assert sim < 0.5


def test_merchant_matcher_find_canonical():
    """Test finding canonical name for a payee."""
    matcher = MerchantMatcher()

    # Add known merchant group
    matcher.canonical_names["woolworths"] = MerchantGroup(
        canonical_name="Woolworths",
        variations={"woolworths", "woolworth", "woolies"},
    )

    # Should find exact match
    result = matcher.find_canonical("woolworths")
    assert result == "Woolworths"

    # Should find similar variation
    result = matcher.find_canonical("woolworth")
    assert result == "Woolworths"

    # Should return None for unknown
    result = matcher.find_canonical("coles")
    assert result is None


def test_merchant_matcher_add_variation():
    """Test adding a variation to a merchant group."""
    matcher = MerchantMatcher()

    # Create new group
    matcher.add_variation("Woolworths", "woolworths pty ltd")
    assert "woolworths" in matcher.canonical_names
    assert matcher.canonical_names["woolworths"].canonical_name == "Woolworths"

    # Add to existing group
    matcher.add_variation("Woolworths", "woolies")
    group = matcher.canonical_names["woolworths"]
    assert "woolies" in group.variations
    assert len(group.variations) == 2


def test_merchant_matcher_suggest_matches():
    """Test suggesting potential matches for a payee."""
    matcher = MerchantMatcher()

    matcher.add_variation("Woolworths", "woolworths pty ltd")
    matcher.add_variation("Coles", "coles supermarkets")

    # Should suggest Woolworths for similar name
    suggestions = matcher.suggest_matches("woolworth", threshold=0.8)
    assert len(suggestions) > 0
    assert suggestions[0][0] == "Woolworths"
    assert suggestions[0][1] > 0.8

    # Should not suggest if below threshold
    suggestions = matcher.suggest_matches("aldi", threshold=0.8)
    assert len(suggestions) == 0
