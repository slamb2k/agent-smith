"""Tests for rule engine."""

import pytest
import uuid
import tempfile
from datetime import datetime
from pathlib import Path
from scripts.core.rule_engine import Rule, RuleEngine, RuleType, IntelligenceMode


def test_rule_initialization_with_minimal_fields():
    """Test Rule can be created with minimal required fields."""
    rule = Rule(
        name="Test Rule",
        payee_regex="WOOLWORTHS.*",
        category_id=12345,
    )

    assert rule.name == "Test Rule"
    assert rule.payee_regex == "WOOLWORTHS.*"
    assert rule.category_id == 12345
    assert rule.rule_type == RuleType.LOCAL
    assert rule.confidence == 100
    assert rule.priority == 100
    assert isinstance(rule.rule_id, str)
    assert len(rule.rule_id) == 36  # UUID format


def test_rule_initialization_with_all_fields():
    """Test Rule initialization with all optional fields."""
    rule_id = str(uuid.uuid4())
    rule = Rule(
        rule_id=rule_id,
        name="Complex Rule",
        payee_regex="COLES.*",
        category_id=12346,
        rule_type=RuleType.SESSION,
        amount_min=10.0,
        amount_max=500.0,
        account_ids=[1, 2, 3],
        excludes=["COLES PETROL"],
        confidence=95,
        priority=200,
        requires_approval=True,
        tags=["groceries", "test"],
    )

    assert rule.rule_id == rule_id
    assert rule.name == "Complex Rule"
    assert rule.amount_min == 10.0
    assert rule.amount_max == 500.0
    assert rule.account_ids == [1, 2, 3]
    assert rule.excludes == ["COLES PETROL"]
    assert rule.confidence == 95
    assert rule.priority == 200
    assert rule.requires_approval is True
    assert rule.tags == ["groceries", "test"]


def test_rule_matches_simple_payee():
    """Test rule matches transaction with simple payee pattern."""
    rule = Rule(
        name="Woolworths",
        payee_regex="WOOLWORTHS.*",
        category_id=12345,
    )

    transaction = {
        "payee": "WOOLWORTHS EPPING",
        "amount": "-50.00",
    }

    assert rule.match_transaction(transaction) is True


def test_rule_does_not_match_different_payee():
    """Test rule doesn't match transaction with different payee."""
    rule = Rule(
        name="Woolworths",
        payee_regex="WOOLWORTHS.*",
        category_id=12345,
    )

    transaction = {
        "payee": "COLES SUPERMARKET",
        "amount": "-50.00",
    }

    assert rule.match_transaction(transaction) is False


def test_rule_matches_with_amount_range():
    """Test rule matches only within amount range."""
    rule = Rule(
        name="Small Purchases",
        payee_regex=".*",
        category_id=12345,
        amount_min=10.0,
        amount_max=100.0,
    )

    # Within range
    assert rule.match_transaction({"payee": "TEST", "amount": "-50.00"}) is True

    # Below range
    assert rule.match_transaction({"payee": "TEST", "amount": "-5.00"}) is False

    # Above range
    assert rule.match_transaction({"payee": "TEST", "amount": "-150.00"}) is False


def test_rule_excludes_pattern():
    """Test rule excludes transactions matching exclusion pattern."""
    rule = Rule(
        name="Woolworths Non-Petrol",
        payee_regex="WOOLWORTHS.*",
        category_id=12345,
        excludes=["WOOLWORTHS PETROL"],
    )

    # Should match
    assert rule.match_transaction({"payee": "WOOLWORTHS EPPING", "amount": "-50.00"}) is True

    # Should be excluded
    assert rule.match_transaction({"payee": "WOOLWORTHS PETROL", "amount": "-50.00"}) is False


def test_rule_engine_saves_and_loads_rules(tmp_path):
    """Test RuleEngine can save and load rules from JSON."""
    rules_file = tmp_path / "test_rules.json"

    # Create engine and add rules
    engine = RuleEngine(rules_file=rules_file)
    rule1 = Rule(name="Woolworths", payee_regex="WOOLWORTHS.*", category_id=100)
    rule2 = Rule(name="Coles", payee_regex="COLES.*", category_id=200)

    engine.add_rule(rule1)
    engine.add_rule(rule2)
    engine.save_rules()

    # Create new engine and load
    engine2 = RuleEngine(rules_file=rules_file)

    assert len(engine2.rules) == 2
    assert engine2.rules[0].name == "Woolworths"
    assert engine2.rules[1].name == "Coles"


def test_rule_engine_handles_missing_file():
    """Test RuleEngine handles missing rules file gracefully."""
    import tempfile

    rules_file = Path(tempfile.gettempdir()) / "nonexistent_rules.json"

    if rules_file.exists():
        rules_file.unlink()

    engine = RuleEngine(rules_file=rules_file)
    assert len(engine.rules) == 0


def test_intelligence_mode_conservative():
    """Test conservative mode requires approval for all rules."""
    engine = RuleEngine()
    engine.intelligence_mode = IntelligenceMode.CONSERVATIVE

    high_confidence_rule = Rule(name="Test", payee_regex="TEST.*", category_id=100, confidence=95)

    assert engine.should_auto_apply(high_confidence_rule) is False
    assert engine.should_ask_approval(high_confidence_rule) is True


def test_intelligence_mode_smart():
    """Test smart mode auto-applies high confidence, asks for medium."""
    engine = RuleEngine()
    engine.intelligence_mode = IntelligenceMode.SMART

    high_confidence = Rule(name="High", payee_regex="TEST.*", category_id=100, confidence=95)
    medium_confidence = Rule(name="Med", payee_regex="TEST.*", category_id=100, confidence=80)
    low_confidence = Rule(name="Low", payee_regex="TEST.*", category_id=100, confidence=60)

    assert engine.should_auto_apply(high_confidence) is True
    assert engine.should_ask_approval(high_confidence) is False

    assert engine.should_auto_apply(medium_confidence) is False
    assert engine.should_ask_approval(medium_confidence) is True

    assert engine.should_auto_apply(low_confidence) is False
    assert engine.should_ask_approval(low_confidence) is False


def test_intelligence_mode_aggressive():
    """Test aggressive mode auto-applies medium+ confidence."""
    engine = RuleEngine()
    engine.intelligence_mode = IntelligenceMode.AGGRESSIVE

    medium_confidence = Rule(name="Med", payee_regex="TEST.*", category_id=100, confidence=80)
    low_confidence = Rule(name="Low", payee_regex="TEST.*", category_id=100, confidence=55)
    very_low = Rule(name="VLow", payee_regex="TEST.*", category_id=100, confidence=40)

    assert engine.should_auto_apply(medium_confidence) is True
    assert engine.should_ask_approval(medium_confidence) is False

    assert engine.should_auto_apply(low_confidence) is False
    assert engine.should_ask_approval(low_confidence) is True

    assert engine.should_auto_apply(very_low) is False
    assert engine.should_ask_approval(very_low) is False


def test_find_matching_rules_returns_sorted_by_priority():
    """Test find_matching_rules returns rules sorted by priority (highest first)."""
    engine = RuleEngine()

    low_priority = Rule(name="Low", payee_regex="TEST.*", category_id=100, priority=50)
    high_priority = Rule(name="High", payee_regex="TEST.*", category_id=200, priority=200)
    medium_priority = Rule(name="Med", payee_regex="TEST.*", category_id=150, priority=100)

    engine.add_rule(low_priority)
    engine.add_rule(high_priority)
    engine.add_rule(medium_priority)

    transaction = {"payee": "TEST MERCHANT", "amount": "-50.00"}
    matches = engine.find_matching_rules(transaction)

    assert len(matches) == 3
    assert matches[0].name == "High"
    assert matches[1].name == "Med"
    assert matches[2].name == "Low"


def test_find_matching_rules_returns_empty_for_no_match():
    """Test find_matching_rules returns empty list when no rules match."""
    engine = RuleEngine()
    engine.add_rule(Rule(name="Woolworths", payee_regex="WOOLWORTHS.*", category_id=100))

    transaction = {"payee": "COLES SUPERMARKET", "amount": "-50.00"}
    matches = engine.find_matching_rules(transaction)

    assert len(matches) == 0


def test_find_best_match_returns_highest_priority():
    """Test find_best_match returns highest priority matching rule."""
    engine = RuleEngine()

    low_priority = Rule(name="Low", payee_regex="TEST.*", category_id=100, priority=50)
    high_priority = Rule(name="High", payee_regex="TEST.*", category_id=200, priority=200)

    engine.add_rule(low_priority)
    engine.add_rule(high_priority)

    transaction = {"payee": "TEST MERCHANT", "amount": "-50.00"}
    best = engine.find_best_match(transaction)

    assert best is not None
    assert best.name == "High"


def test_find_best_match_returns_none_for_no_match():
    """Test find_best_match returns None when no rules match."""
    engine = RuleEngine()
    engine.add_rule(Rule(name="Woolworths", payee_regex="WOOLWORTHS.*", category_id=100))

    transaction = {"payee": "COLES SUPERMARKET", "amount": "-50.00"}
    best = engine.find_best_match(transaction)

    assert best is None


def test_record_match_increments_counter_and_updates_timestamp():
    """Test record_match() increments matches counter and updates last_used."""
    rule = Rule(name="Test", payee_regex="TEST.*", category_id=100)

    assert rule.matches == 0
    assert rule.last_used is None

    rule.record_match()

    assert rule.matches == 1
    assert rule.last_used is not None


def test_record_application_increments_counter_and_updates_timestamp():
    """Test record_application() increments applied counter and updates last_used."""
    rule = Rule(name="Test", payee_regex="TEST.*", category_id=100)

    assert rule.applied == 0
    assert rule.last_used is None

    rule.record_application()

    assert rule.applied == 1
    assert rule.last_used is not None


def test_record_override_increments_counter():
    """Test record_override() increments user_overrides counter."""
    rule = Rule(name="Test", payee_regex="TEST.*", category_id=100)

    assert rule.user_overrides == 0

    rule.record_override()

    assert rule.user_overrides == 1


def test_get_accuracy_calculates_percentage():
    """Test get_accuracy() calculates accuracy percentage."""
    rule = Rule(name="Test", payee_regex="TEST.*", category_id=100)

    # Apply 10 times successfully
    for _ in range(10):
        rule.record_application()

    assert rule.get_accuracy() == 100.0

    # User overrides 1
    rule.record_override()

    # 9 successful out of 10 = 90%
    assert abs(rule.get_accuracy() - 90.0) < 0.1


def test_get_accuracy_handles_zero_matches():
    """Test get_accuracy() handles division by zero."""
    rule = Rule(name="Test", payee_regex="TEST.*", category_id=100)

    # No applications yet
    assert rule.get_accuracy() == 0.0
