"""Integration tests for rule engine with real API and end-to-end workflows.

These tests require:
- Valid POCKETSMITH_API_KEY in .env
- Active internet connection
- Run with: pytest -m integration
"""

import os
import pytest
import tempfile
from pathlib import Path
from scripts.core.rule_engine import Rule, RuleEngine, IntelligenceMode, RuleType
from scripts.core.api_client import PocketSmithClient
from scripts.operations.categorize import categorize_transaction, categorize_batch
from scripts.utils.merchant_normalizer import MerchantNormalizer


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def api_client():
    """Create API client with real credentials."""
    api_key = os.getenv("POCKETSMITH_API_KEY")
    if not api_key:
        pytest.skip("POCKETSMITH_API_KEY not set - skipping integration tests")

    return PocketSmithClient(api_key=api_key)


@pytest.fixture
def temp_rules_file():
    """Create temporary rules file for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    temp_file.write("[]")
    temp_file.close()
    yield Path(temp_file.name)
    # Cleanup
    if Path(temp_file.name).exists():
        Path(temp_file.name).unlink()


def test_rule_engine_end_to_end_workflow(api_client, temp_rules_file):
    """Test complete rule engine workflow: create rules, match transactions, track performance."""
    # Initialize rule engine with temporary file
    engine = RuleEngine(rules_file=temp_rules_file)
    engine.api_client = api_client
    engine.intelligence_mode = IntelligenceMode.SMART

    # Get user and some transactions
    user = api_client.get_user()
    transactions = api_client.get_transactions(
        user_id=user["id"], start_date="2024-01-01", end_date="2024-12-31", per_page=10
    )

    assert len(transactions) > 0, "Need at least 1 transaction for integration test"

    # Create a test rule matching first transaction
    test_txn = transactions[0]
    payee = test_txn.get("payee", "")

    if payee:
        # Create rule with partial payee match
        payee_prefix = payee.split()[0] if " " in payee else payee[:10]
        rule = Rule(
            name=f"Test Rule - {payee_prefix}",
            payee_regex=f"{payee_prefix}.*",
            category_id=test_txn.get("category", {}).get("id", 0),
            confidence=95,
        )
        engine.add_rule(rule)

        # Save rules to file
        engine.save_rules()

        # Test categorization (dry-run to avoid mutations)
        result = categorize_transaction(test_txn, engine, api_client, dry_run=True)

        assert result["matched"] is True, "Rule should match transaction"
        assert result["rule_name"] == rule.name
        assert result["confidence"] == 95
        assert result["auto_applied"] is True, "High confidence should auto-apply in SMART mode"

        # Reload engine from file
        engine2 = RuleEngine(rules_file=temp_rules_file)
        assert len(engine2.rules) == 1, "Rule should persist and reload"
        assert engine2.rules[0].name == rule.name

        print("✓ End-to-end workflow successful: rule created, matched, and persisted")


def test_rule_matching_with_multiple_transactions(api_client, temp_rules_file):
    """Test rule matching against multiple real transactions."""
    engine = RuleEngine(rules_file=temp_rules_file)
    engine.intelligence_mode = IntelligenceMode.SMART

    # Get transactions
    user = api_client.get_user()
    transactions = api_client.get_transactions(
        user_id=user["id"], start_date="2024-01-01", end_date="2024-12-31", per_page=20
    )

    if len(transactions) < 5:
        pytest.skip("Need at least 5 transactions for this test")

    # Create rules for first few unique payees
    unique_payees = set()
    for txn in transactions:
        payee = txn.get("payee", "")
        if payee and payee not in unique_payees:
            unique_payees.add(payee)
            payee_prefix = payee.split()[0] if " " in payee else payee[:10]
            rule = Rule(
                name=f"Rule - {payee_prefix}",
                payee_regex=f"{payee_prefix}.*",
                category_id=txn.get("category", {}).get("id", 0),
                confidence=90,
            )
            engine.add_rule(rule)

            if len(unique_payees) >= 3:
                break

    # Test batch categorization (dry-run)
    results = categorize_batch(transactions, engine, api_client, dry_run=True)

    matched_count = sum(1 for r in results if r["matched"])
    assert matched_count >= 3, f"Should match at least 3 transactions, got {matched_count}"

    print(f"✓ Batch categorization: {len(transactions)} transactions, {matched_count} matched")


def test_intelligence_mode_affects_auto_apply(api_client, temp_rules_file):
    """Test that intelligence modes correctly control auto-apply behavior."""
    user = api_client.get_user()
    transactions = api_client.get_transactions(
        user_id=user["id"], start_date="2024-01-01", end_date="2024-12-31", per_page=10
    )

    if not transactions:
        pytest.skip("Need at least 1 transaction for this test")

    test_txn = transactions[0]
    payee = test_txn.get("payee", "")
    if not payee:
        pytest.skip("Transaction needs payee for this test")

    payee_prefix = payee.split()[0] if " " in payee else payee[:10]

    # Test with medium confidence rule (80%)
    medium_confidence_rule = Rule(
        name=f"Medium Confidence - {payee_prefix}",
        payee_regex=f"{payee_prefix}.*",
        category_id=test_txn.get("category", {}).get("id", 0),
        confidence=80,
    )

    # Conservative mode - should require approval
    engine_conservative = RuleEngine(rules_file=temp_rules_file)
    engine_conservative.intelligence_mode = IntelligenceMode.CONSERVATIVE
    engine_conservative.add_rule(medium_confidence_rule)

    result = categorize_transaction(test_txn, engine_conservative, api_client, dry_run=True)
    assert result["matched"] is True
    assert result["auto_applied"] is False, "Conservative should never auto-apply"
    assert result["requires_approval"] is True

    # Smart mode - should require approval (80% < 90% threshold)
    engine_smart = RuleEngine(rules_file=temp_rules_file)
    engine_smart.intelligence_mode = IntelligenceMode.SMART
    engine_smart.add_rule(medium_confidence_rule)

    result = categorize_transaction(test_txn, engine_smart, api_client, dry_run=True)
    assert result["matched"] is True
    assert result["auto_applied"] is False
    assert result["requires_approval"] is True

    # Aggressive mode - should auto-apply (80% >= 80% threshold)
    engine_aggressive = RuleEngine(rules_file=temp_rules_file)
    engine_aggressive.intelligence_mode = IntelligenceMode.AGGRESSIVE
    engine_aggressive.add_rule(medium_confidence_rule)

    result = categorize_transaction(test_txn, engine_aggressive, api_client, dry_run=True)
    assert result["matched"] is True
    assert result["auto_applied"] is True, "Aggressive should auto-apply 80%+ confidence"

    print("✓ Intelligence modes working correctly: Conservative < Smart < Aggressive")


def test_merchant_normalization_with_real_transactions(api_client):
    """Test merchant normalization learns from real transaction data."""
    normalizer = MerchantNormalizer()

    user = api_client.get_user()
    transactions = api_client.get_transactions(
        user_id=user["id"], start_date="2024-01-01", end_date="2024-12-31", per_page=50
    )

    if len(transactions) < 10:
        pytest.skip("Need at least 10 transactions for merchant learning")

    # Learn patterns from transactions
    normalizer.learn_from_transactions(transactions)

    # Should have learned some merchant patterns
    assert len(normalizer.mappings) > 0, "Should learn at least one merchant pattern"

    # Test normalization on sample transactions
    if transactions:
        sample = transactions[0]
        payee = sample.get("payee", "")
        if payee:
            normalized = normalizer.normalize(payee)
            canonical = normalizer.get_canonical_name(payee)

            # Normalized should be cleaned up (upper case, no trailing spaces)
            assert normalized == normalized.upper().strip()
            assert canonical, "Should have a canonical name"

            print(f"✓ Merchant normalization: '{payee}' → '{normalized}' → '{canonical}'")
            print(f"✓ Learned {len(normalizer.mappings)} merchant patterns")


def test_merchant_normalization_integration_with_rules(api_client, temp_rules_file):
    """Test merchant normalization integrates with rule matching."""
    normalizer = MerchantNormalizer()
    engine = RuleEngine(rules_file=temp_rules_file)

    user = api_client.get_user()
    transactions = api_client.get_transactions(
        user_id=user["id"], start_date="2024-01-01", end_date="2024-12-31", per_page=30
    )

    if len(transactions) < 5:
        pytest.skip("Need at least 5 transactions for this test")

    # Learn merchant patterns
    normalizer.learn_from_transactions(transactions)

    # Create rules using canonical names
    canonical_names = list(normalizer.mappings.keys())[:3]
    if not canonical_names:
        pytest.skip("No merchant patterns learned")

    for canonical in canonical_names:
        rule = Rule(
            name=f"Rule - {canonical}",
            payee_regex=f"{canonical}.*",
            category_id=12345,  # Dummy category
            confidence=85,
        )
        engine.add_rule(rule)

    # Test that normalized payees match rules
    matches_found = 0
    for txn in transactions[:20]:
        payee = txn.get("payee", "")
        if not payee:
            continue

        # Normalize the payee
        canonical = normalizer.get_canonical_name(payee)

        # Create transaction with normalized payee for matching
        normalized_txn = {**txn, "payee": canonical}

        # Check if rule matches
        matching_rules = engine.find_matching_rules(normalized_txn)
        if matching_rules:
            matches_found += 1

    assert matches_found > 0, "Should find matches using normalized merchant names"
    print(f"✓ Merchant normalization + rule matching: {matches_found} matches in 20 transactions")


def test_rule_performance_tracking_over_multiple_matches(api_client, temp_rules_file):
    """Test that rule performance metrics are tracked correctly over multiple operations."""
    engine = RuleEngine(rules_file=temp_rules_file)
    # Use CONSERVATIVE mode so rules require approval (calls record_match in dry_run)
    engine.intelligence_mode = IntelligenceMode.CONSERVATIVE

    user = api_client.get_user()
    transactions = api_client.get_transactions(
        user_id=user["id"], start_date="2024-01-01", end_date="2024-12-31", per_page=15
    )

    if len(transactions) < 3:
        pytest.skip("Need at least 3 transactions for performance tracking test")

    # Create a very broad rule that will match most transactions
    # Use a wildcard pattern that matches anything
    rule = Rule(
        name="Performance Test - Catch All",
        payee_regex=".*",  # Matches everything
        category_id=12345,
        confidence=95,
    )
    engine.add_rule(rule)

    # Process transactions (dry-run)
    # In CONSERVATIVE mode, all matches require approval and call record_match()
    initial_matches = rule.matches

    results = categorize_batch(transactions, engine, api_client, dry_run=True)

    # Check performance was tracked - with catch-all pattern, we should get matches
    matched_count = sum(1 for r in results if r["matched"])
    approval_count = sum(1 for r in results if r["requires_approval"])

    assert matched_count > 0, "Catch-all pattern should match at least some transactions"
    assert approval_count > 0, "Conservative mode should require approval"
    assert (
        rule.matches > initial_matches
    ), "Match counter should increment in dry-run with requires_approval"
    assert rule.last_used is not None, "Last used should be set"

    # Calculate accuracy
    accuracy = rule.get_accuracy()
    assert 0 <= accuracy <= 100, "Accuracy should be between 0 and 100"

    print(
        f"✓ Performance tracking: {rule.matches} matches, "
        f"{approval_count} require approval, {accuracy:.1f}% accuracy"
    )


def test_rule_priority_sorting_in_real_scenario(api_client, temp_rules_file):
    """Test that rule priority correctly determines best match with real data."""
    engine = RuleEngine(rules_file=temp_rules_file)

    user = api_client.get_user()
    transactions = api_client.get_transactions(
        user_id=user["id"], start_date="2024-01-01", end_date="2024-12-31", per_page=10
    )

    if not transactions:
        pytest.skip("Need at least 1 transaction for this test")

    test_txn = transactions[0]
    payee = test_txn.get("payee", "")
    if not payee:
        pytest.skip("Transaction needs payee for this test")

    # Create multiple rules with different priorities that match same transaction
    payee_prefix = payee.split()[0] if " " in payee else payee[:10]

    # Low priority rule
    low_priority = Rule(
        name="Low Priority",
        payee_regex=f"{payee_prefix}.*",
        category_id=100,
        priority=50,
        confidence=90,
    )

    # High priority rule
    high_priority = Rule(
        name="High Priority",
        payee_regex=f"{payee_prefix}.*",
        category_id=200,
        priority=200,
        confidence=90,
    )

    # Medium priority rule
    medium_priority = Rule(
        name="Medium Priority",
        payee_regex=f"{payee_prefix}.*",
        category_id=150,
        priority=100,
        confidence=90,
    )

    # Add in non-priority order
    engine.add_rule(low_priority)
    engine.add_rule(high_priority)
    engine.add_rule(medium_priority)

    # Find all matching rules
    matches = engine.find_matching_rules(test_txn)
    assert len(matches) == 3, "All three rules should match"

    # Verify sorting by priority
    assert matches[0].name == "High Priority", "Highest priority should be first"
    assert matches[1].name == "Medium Priority", "Medium priority should be second"
    assert matches[2].name == "Low Priority", "Lowest priority should be last"

    # Best match should be highest priority
    best = engine.find_best_match(test_txn)
    assert best.name == "High Priority", "Best match should be highest priority rule"
    assert best.category_id == 200

    print("✓ Rule priority sorting working correctly with real transactions")


def test_rule_persistence_with_performance_metrics(api_client, temp_rules_file):
    """Test that rule performance metrics persist correctly across save/load cycles."""
    # Create engine and rule
    engine1 = RuleEngine(rules_file=temp_rules_file)

    user = api_client.get_user()
    transactions = api_client.get_transactions(
        user_id=user["id"], start_date="2024-01-01", end_date="2024-12-31", per_page=10
    )

    if not transactions:
        pytest.skip("Need at least 1 transaction for this test")

    test_txn = transactions[0]
    payee = test_txn.get("payee", "")
    if not payee:
        pytest.skip("Transaction needs payee for this test")

    payee_prefix = payee.split()[0] if " " in payee else payee[:10]
    rule = Rule(
        name=f"Persistence Test - {payee_prefix}",
        payee_regex=f"{payee_prefix}.*",
        category_id=12345,
        confidence=95,
    )
    engine1.add_rule(rule)

    # Process some transactions to generate metrics
    categorize_batch(transactions, engine1, api_client, dry_run=True)

    # Save state
    initial_matches = rule.matches
    initial_applied = rule.applied
    initial_last_used = rule.last_used
    engine1.save_rules()

    # Load into new engine
    engine2 = RuleEngine(rules_file=temp_rules_file)

    assert len(engine2.rules) == 1, "Rule should be loaded"
    loaded_rule = engine2.rules[0]

    # Verify performance metrics persisted
    assert loaded_rule.matches == initial_matches, "Match count should persist"
    assert loaded_rule.applied == initial_applied, "Applied count should persist"
    assert loaded_rule.last_used == initial_last_used, "Last used should persist"

    print(
        f"✓ Rule persistence: metrics saved and loaded "
        f"({loaded_rule.matches} matches, {loaded_rule.applied} applied)"
    )
