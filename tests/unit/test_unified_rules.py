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
