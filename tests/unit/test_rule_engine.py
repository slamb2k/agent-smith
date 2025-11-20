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


def test_get_accuracy_handles_zero_applications():
    """Test get_accuracy() handles division by zero when no applications."""
    rule = Rule(name="Test", payee_regex="TEST.*", category_id=100)

    # No applications yet - should return 100.0 (innocent until proven guilty)
    assert rule.get_accuracy() == 100.0


def test_get_accuracy_with_unapplied_matches():
    """Test accuracy calculation when matches > applied."""
    rule = Rule(name="Test", payee_regex="TEST.*", category_id=100)

    # Match 5 times but only apply 3
    rule.record_match()  # match only
    rule.record_match()  # match only
    rule.record_application()  # match + apply
    rule.record_application()  # match + apply
    rule.record_application()  # match + apply

    # 3 applications, 0 overrides = 100% accuracy of applications
    assert rule.get_accuracy() == 100.0

    # Override one
    rule.record_override()

    # 2 successful out of 3 applied = 66.67%
    assert abs(rule.get_accuracy() - 66.67) < 0.1


def test_sync_platform_rules_fetches_from_api(tmp_path):
    """Test sync_platform_rules fetches category rules from API."""
    from unittest.mock import Mock

    platform_rules_file = tmp_path / "platform_rules.json"
    engine = RuleEngine()
    engine.platform_rules_file = platform_rules_file

    # Mock API client
    mock_client = Mock()
    mock_client.get_user.return_value = {"id": 123}
    mock_client.get_categories.return_value = [
        {"id": 100, "title": "Groceries"},
        {"id": 200, "title": "Transport"},
    ]
    mock_client.get_category_rules.return_value = [
        {"id": 1, "payee_matches": "WOOLWORTHS", "category_id": 100},
        {"id": 2, "payee_matches": "COLES", "category_id": 100},
    ]

    # Sync platform rules
    engine.sync_platform_rules(mock_client)

    # Verify API calls
    mock_client.get_user.assert_called_once()
    mock_client.get_categories.assert_called_once_with(user_id=123)
    assert mock_client.get_category_rules.call_count == 2

    # Verify platform rules file created
    assert platform_rules_file.exists()


def test_sync_platform_rules_updates_tracking_file(tmp_path):
    """Test sync_platform_rules updates platform_rules.json."""
    from unittest.mock import Mock
    import json

    platform_rules_file = tmp_path / "platform_rules.json"
    engine = RuleEngine()
    engine.platform_rules_file = platform_rules_file

    # Mock API client
    mock_client = Mock()
    mock_client.get_user.return_value = {"id": 123}
    mock_client.get_categories.return_value = [
        {"id": 100, "title": "Groceries"},
    ]
    mock_client.get_category_rules.return_value = [
        {"id": 1, "payee_matches": "WOOLWORTHS"},
    ]

    # Sync platform rules
    engine.sync_platform_rules(mock_client)

    # Read tracking file
    with open(platform_rules_file) as f:
        platform_rules = json.load(f)

    # Verify structure
    assert len(platform_rules) == 1
    assert platform_rules[0]["rule_id"] == 1
    assert platform_rules[0]["category_id"] == 100
    assert platform_rules[0]["payee_contains"] == "WOOLWORTHS"
    assert "synced_at" in platform_rules[0]


def test_create_platform_rule_creates_via_api(tmp_path):
    """Test create_platform_rule creates rule via API and tracks it."""
    from unittest.mock import Mock
    import json

    platform_rules_file = tmp_path / "platform_rules.json"
    platform_rules_file.write_text("[]")

    engine = RuleEngine()
    engine.platform_rules_file = platform_rules_file

    # Mock API client
    mock_client = Mock()
    mock_client.create_category_rule.return_value = {"id": 999}

    # Create platform rule
    result = engine.create_platform_rule(mock_client, category_id=100, payee_contains="WOOLWORTHS")

    # Verify API call
    mock_client.create_category_rule.assert_called_once_with(
        category_id=100, payee_matches="WOOLWORTHS"
    )

    # Verify result
    assert result["rule_id"] == 999
    assert result["category_id"] == 100
    assert result["payee_contains"] == "WOOLWORTHS"

    # Verify tracking file updated
    with open(platform_rules_file) as f:
        platform_rules = json.load(f)

    assert len(platform_rules) == 1
    assert platform_rules[0]["rule_id"] == 999


def test_create_platform_rule_appends_to_existing_tracking(tmp_path):
    """Test create_platform_rule appends to existing platform rules."""
    from unittest.mock import Mock
    import json

    platform_rules_file = tmp_path / "platform_rules.json"

    # Create existing tracking file
    existing_rules = [
        {
            "rule_id": 1,
            "category_id": 100,
            "payee_contains": "COLES",
            "created_at": "2025-11-20T10:00:00",
        }
    ]
    platform_rules_file.write_text(json.dumps(existing_rules))

    engine = RuleEngine()
    engine.platform_rules_file = platform_rules_file

    # Mock API client
    mock_client = Mock()
    mock_client.create_category_rule.return_value = {"id": 2}

    # Create new platform rule
    engine.create_platform_rule(mock_client, category_id=200, payee_contains="WOOLWORTHS")

    # Verify tracking file has both rules
    with open(platform_rules_file) as f:
        platform_rules = json.load(f)

    assert len(platform_rules) == 2
    assert platform_rules[0]["rule_id"] == 1
    assert platform_rules[1]["rule_id"] == 2
