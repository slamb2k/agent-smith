"""Unit tests for benchmarking module."""

import pytest
from scripts.features.benchmarking import BenchmarkEngine, PeerCriteria


def test_benchmark_engine_initialization():
    """Test creating benchmark engine."""
    engine = BenchmarkEngine()
    assert engine is not None


def test_benchmark_engine_anonymize_user():
    """Test anonymizing user data."""
    engine = BenchmarkEngine()

    # Same input should produce same hash
    hash1 = engine.anonymize_user_id("user_123")
    hash2 = engine.anonymize_user_id("user_123")
    assert hash1 == hash2

    # Different inputs should produce different hashes
    hash3 = engine.anonymize_user_id("user_456")
    assert hash1 != hash3

    # Hash should be fixed length
    assert len(hash1) == 64  # SHA-256 hex digest


def test_benchmark_engine_add_data_point():
    """Test adding anonymized data points."""
    engine = BenchmarkEngine()

    engine.add_data_point(
        category="Groceries",
        amount=500.00,
        user_id="user_123",
        criteria=PeerCriteria(household_size=2, income_bracket="50k-75k"),
    )

    # Should be stored under anonymized key
    key = engine._build_key("Groceries", PeerCriteria(household_size=2, income_bracket="50k-75k"))
    assert key in engine.aggregated_data
    assert 500.00 in engine.aggregated_data[key]


def test_benchmark_engine_compare():
    """Test comparing user spending to peer group."""
    engine = BenchmarkEngine()

    criteria = PeerCriteria(household_size=2, income_bracket="50k-75k")

    # Add peer data (5 peers)
    peer_amounts = [400.00, 450.00, 500.00, 550.00, 600.00]
    for i, amount in enumerate(peer_amounts):
        engine.add_data_point(
            category="Groceries", amount=amount, user_id=f"peer_{i}", criteria=criteria
        )

    # Compare user at median
    result = engine.compare(category="Groceries", user_amount=500.00, criteria=criteria)

    assert result.category == "Groceries"
    assert result.user_amount == 500.00
    assert result.peer_average == 500.00  # Mean of peer_amounts
    assert result.peer_median == 500.00
    assert result.percentile == 50  # At median
    assert result.peer_count == 5


def test_benchmark_engine_percentile_calculation():
    """Test percentile calculation."""
    engine = BenchmarkEngine()

    criteria = PeerCriteria(household_size=2)

    # Add peer data
    amounts = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    for i, amount in enumerate(amounts):
        engine.add_data_point(
            category="Dining", amount=float(amount), user_id=f"peer_{i}", criteria=criteria
        )

    # User spending $250 should be ~25th percentile
    result = engine.compare(category="Dining", user_amount=250.00, criteria=criteria)
    assert 20 <= result.percentile <= 30

    # User spending $750 should be ~75th percentile
    result = engine.compare(category="Dining", user_amount=750.00, criteria=criteria)
    assert 70 <= result.percentile <= 80
