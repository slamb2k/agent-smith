"""Tests for unified YAML rule system."""

import pytest
from pathlib import Path
from scripts.core.unified_rules import UnifiedRuleEngine, RuleType


def test_parse_category_rule(tmp_path):
    """Test parsing a category rule from YAML."""
    rules_file = tmp_path / "test_rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: WOOLWORTHS → Groceries
    patterns: [WOOLWORTHS, COLES]
    category: Groceries
    confidence: 95
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)

    assert len(engine.category_rules) == 1
    rule = engine.category_rules[0]
    assert rule.name == "WOOLWORTHS → Groceries"
    assert rule.patterns == ["WOOLWORTHS", "COLES"]
    assert rule.category == "Groceries"
    assert rule.confidence == 95


def test_parse_label_rule(tmp_path):
    """Test parsing a label rule from YAML."""
    rules_file = tmp_path / "test_rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: label
    name: Personal Groceries
    when:
      categories: [Groceries]
      accounts: [Personal]
    labels: [Personal, Essential]
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)

    assert len(engine.label_rules) == 1
    rule = engine.label_rules[0]
    assert rule.name == "Personal Groceries"
    assert rule.when_categories == ["Groceries"]
    assert rule.when_accounts == ["Personal"]
    assert rule.labels == ["Personal", "Essential"]


def test_parse_mixed_rules(tmp_path):
    """Test parsing both category and label rules."""
    rules_file = tmp_path / "test_rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: Test Category
    patterns: [TEST]
    category: Test
    confidence: 90

  - type: label
    name: Test Label
    when:
      categories: [Test]
    labels: [TestLabel]
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)

    assert len(engine.category_rules) == 1
    assert len(engine.label_rules) == 1


def test_match_category_rule_by_pattern():
    """Test matching category rule by payee pattern."""
    from scripts.core.unified_rules import CategoryRule

    rule = CategoryRule(
        name="Groceries", patterns=["WOOLWORTHS", "COLES"], category="Groceries", confidence=95
    )

    transaction = {
        "payee": "WOOLWORTHS METRO 123",
        "amount": -45.50,
    }

    assert rule.matches(transaction) is True


def test_match_category_rule_with_exclusion():
    """Test category rule with exclusion pattern."""
    from scripts.core.unified_rules import CategoryRule

    rule = CategoryRule(
        name="Transport",
        patterns=["UBER"],
        exclude_patterns=["UBER EATS"],
        category="Transport",
        confidence=90,
    )

    transaction_match = {"payee": "UBER TRIP ABC123"}
    transaction_exclude = {"payee": "UBER EATS ORDER 456"}

    assert rule.matches(transaction_match) is True
    assert rule.matches(transaction_exclude) is False


def test_match_category_rule_case_insensitive():
    """Test that pattern matching is case-insensitive."""
    from scripts.core.unified_rules import CategoryRule

    rule = CategoryRule(name="Coffee", patterns=["Starbucks"], category="Dining", confidence=90)

    # Test lowercase, uppercase, and mixed case
    assert rule.matches({"payee": "starbucks sydney"}) is True
    assert rule.matches({"payee": "STARBUCKS CBD"}) is True
    assert rule.matches({"payee": "StArBuCkS cafe"}) is True


def test_match_category_rule_amount_operators():
    """Test amount operator comparisons."""
    from scripts.core.unified_rules import CategoryRule

    # Test greater than
    rule_gt = CategoryRule(
        name="Large Purchase",
        patterns=["STORE"],
        category="Shopping",
        amount_operator=">",
        amount_value=100.0,
    )
    assert rule_gt.matches({"payee": "STORE 123", "amount": -150.00}) is True
    assert rule_gt.matches({"payee": "STORE 123", "amount": -50.00}) is False

    # Test less than
    rule_lt = CategoryRule(
        name="Small Purchase",
        patterns=["CAFE"],
        category="Dining",
        amount_operator="<",
        amount_value=20.0,
    )
    assert rule_lt.matches({"payee": "CAFE ABC", "amount": -15.00}) is True
    assert rule_lt.matches({"payee": "CAFE ABC", "amount": -25.00}) is False

    # Test greater than or equal
    rule_gte = CategoryRule(
        name="Medium Purchase",
        patterns=["SHOP"],
        category="Shopping",
        amount_operator=">=",
        amount_value=50.0,
    )
    assert rule_gte.matches({"payee": "SHOP", "amount": -50.00}) is True
    assert rule_gte.matches({"payee": "SHOP", "amount": -60.00}) is True
    assert rule_gte.matches({"payee": "SHOP", "amount": -40.00}) is False


def test_match_category_rule_account_filter():
    """Test account filtering."""
    from scripts.core.unified_rules import CategoryRule

    rule = CategoryRule(
        name="Personal Groceries",
        patterns=["WOOLWORTHS"],
        category="Groceries",
        accounts=["Personal", "Joint"],
    )

    # Should match transactions from specified accounts
    assert rule.matches({"payee": "WOOLWORTHS", "_account_name": "Personal"}) is True
    assert rule.matches({"payee": "WOOLWORTHS", "_account_name": "Joint"}) is True

    # Should not match transactions from other accounts
    assert rule.matches({"payee": "WOOLWORTHS", "_account_name": "Business"}) is False


def test_match_label_rule():
    """Test matching label rule with conditions."""
    from scripts.core.unified_rules import LabelRule

    rule = LabelRule(
        name="Personal Groceries",
        when_categories=["Groceries"],
        when_accounts=["Personal"],
        labels=["Personal", "Essential"],
    )

    transaction = {
        "category": {"title": "Groceries"},
        "_account_name": "Personal",
    }

    assert rule.matches(transaction) is True


def test_match_label_rule_uncategorized():
    """Test label rule matching uncategorized transactions."""
    from scripts.core.unified_rules import LabelRule

    rule = LabelRule(
        name="Flag Uncategorized", when_uncategorized=True, labels=["Needs Categorization"]
    )

    transaction_uncategorized = {"category": None}
    transaction_categorized = {"category": {"title": "Groceries"}}

    assert rule.matches(transaction_uncategorized) is True
    assert rule.matches(transaction_categorized) is False


def test_match_label_rule_multiple_categories():
    """Test label rule matching any of multiple categories."""
    from scripts.core.unified_rules import LabelRule

    rule = LabelRule(
        name="Food Expense", when_categories=["Groceries", "Dining", "Restaurants"], labels=["Food"]
    )

    assert rule.matches({"category": {"title": "Groceries"}}) is True
    assert rule.matches({"category": {"title": "Dining"}}) is True
    assert rule.matches({"category": {"title": "Transport"}}) is False


def test_match_label_rule_amount_condition():
    """Test label rule with amount conditions."""
    from scripts.core.unified_rules import LabelRule

    rule = LabelRule(
        name="Large Purchase",
        when_amount_operator=">",
        when_amount_value=100.0,
        labels=["Large Purchase", "Review"],
    )

    assert rule.matches({"amount": -150.00}) is True
    assert rule.matches({"amount": -50.00}) is False


def test_category_rule_with_normalized_payee():
    """Test category rule matching with merchant normalization.

    This tests that MerchantMatcher normalization is used for matching.
    Without normalization, patterns would need to account for variations.
    With normalization, one pattern matches many variations.
    """
    from scripts.core.unified_rules import CategoryRule

    rule = CategoryRule(
        name="Woolworths", patterns=["woolworths"], category="Groceries", confidence=90
    )

    # These should all match after normalization removes IDs and suffixes
    # Note: The raw payees are different, but normalize to similar base forms
    assert rule.matches({"payee": "WOOLWORTHS 1234"}) is True
    assert rule.matches({"payee": "Woolworths Pty Ltd"}) is True
    assert rule.matches({"payee": "WOOLWORTHS METRO AB12CD34"}) is True

    # Test that exclusion patterns also use normalization
    rule_with_exclusion = CategoryRule(
        name="Uber (not Eats)",
        patterns=["uber"],
        exclude_patterns=["uber eats"],
        category="Transport",
        confidence=90,
    )

    # Should match after normalization strips transaction IDs
    assert rule_with_exclusion.matches({"payee": "UBER *TRIP ABC123"}) is True
    # Should exclude after normalization
    assert rule_with_exclusion.matches({"payee": "UBER EATS ORDER 456789"}) is False


def test_categorize_and_label_basic(tmp_path):
    """Test two-phase categorization and labeling."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: WOOLWORTHS → Groceries
    patterns: [WOOLWORTHS]
    category: Groceries
    confidence: 95

  - type: label
    name: Personal Groceries
    when:
      categories: [Groceries]
      accounts: [Personal]
    labels: [Personal, Essential]

  - type: label
    name: Shared Groceries
    when:
      categories: [Groceries]
      accounts: [Shared Bills]
    labels: [Shared Expense]
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)

    transaction = {
        "id": 123,
        "payee": "WOOLWORTHS METRO",
        "amount": -45.50,
        "_account_name": "Personal",
    }

    result = engine.categorize_and_label(transaction)

    # Phase 1: Category should match
    assert result["category"] == "Groceries"
    assert result["confidence"] == 95
    assert result["matched_rules"] == ["WOOLWORTHS → Groceries"]

    # Phase 2: Only Personal Groceries label should match (not Shared)
    assert "Personal" in result["labels"]
    assert "Essential" in result["labels"]
    assert "Shared Expense" not in result["labels"]


def test_categorize_and_label_multiple_label_matches(tmp_path):
    """Test multiple label rules matching same transaction."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: label
    name: Groceries Label
    when:
      categories: [Groceries]
    labels: [Food]

  - type: label
    name: Large Purchase
    when:
      amount_operator: ">"
      amount_value: 100
    labels: [Large Purchase, Review]
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)

    transaction = {
        "category": {"title": "Groceries"},
        "amount": -150.00,
    }

    result = engine.categorize_and_label(transaction)

    # Both label rules should match
    assert "Food" in result["labels"]
    assert "Large Purchase" in result["labels"]
    assert "Review" in result["labels"]
    # Labels should be deduplicated
    assert len(result["labels"]) == 3


def test_categorize_and_label_no_category_match(tmp_path):
    """Test when no category rule matches."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: WOOLWORTHS → Groceries
    patterns: [WOOLWORTHS]
    category: Groceries
    confidence: 95
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)

    transaction = {
        "id": 123,
        "payee": "UNKNOWN MERCHANT",
        "amount": -45.50,
    }

    result = engine.categorize_and_label(transaction)

    # No category match
    assert result["category"] is None
    assert result["confidence"] is None
    assert result["matched_rules"] == []


def test_categorize_and_label_no_label_match(tmp_path):
    """Test when category matches but no label rules match."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: WOOLWORTHS → Groceries
    patterns: [WOOLWORTHS]
    category: Groceries
    confidence: 95

  - type: label
    name: Large Purchase
    when:
      amount_operator: ">"
      amount_value: 100
    labels: [Large Purchase]
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)

    transaction = {
        "id": 123,
        "payee": "WOOLWORTHS METRO",
        "amount": -45.50,
    }

    result = engine.categorize_and_label(transaction)

    # Category should match
    assert result["category"] == "Groceries"
    assert result["confidence"] == 95

    # No label match (amount too small)
    assert result["labels"] == []


def test_categorize_and_label_first_category_match_only(tmp_path):
    """Test that only FIRST matching category rule is returned (short-circuit)."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: category
    name: WOOLWORTHS → Groceries
    patterns: [WOOLWORTHS]
    category: Groceries
    confidence: 95

  - type: category
    name: WOOLWORTHS → Shopping
    patterns: [WOOLWORTHS]
    category: Shopping
    confidence: 80
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)

    transaction = {
        "id": 123,
        "payee": "WOOLWORTHS METRO",
        "amount": -45.50,
    }

    result = engine.categorize_and_label(transaction)

    # Should return FIRST match only
    assert result["category"] == "Groceries"
    assert result["confidence"] == 95
    assert len(result["matched_rules"]) == 1
    assert result["matched_rules"][0] == "WOOLWORTHS → Groceries"


def test_categorize_and_label_deduplicates_labels(tmp_path):
    """Test that duplicate labels are deduplicated."""
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text(
        """
rules:
  - type: label
    name: Rule 1
    when:
      categories: [Groceries]
    labels: [Food, Essential]

  - type: label
    name: Rule 2
    when:
      categories: [Groceries]
    labels: [Essential, Personal]
"""
    )

    engine = UnifiedRuleEngine(rules_file=rules_file)

    transaction = {
        "category": {"title": "Groceries"},
    }

    result = engine.categorize_and_label(transaction)

    # Essential appears in both rules but should only appear once
    assert result["labels"].count("Essential") == 1
    assert "Food" in result["labels"]
    assert "Essential" in result["labels"]
    assert "Personal" in result["labels"]
    assert len(result["labels"]) == 3
