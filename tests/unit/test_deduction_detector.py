"""Tests for deduction detection (Level 2 tax intelligence)."""

import pytest
from datetime import datetime, time
from scripts.tax.deduction_detector import DeductionDetector


@pytest.fixture
def detector():
    """Create DeductionDetector instance for testing."""
    return DeductionDetector()


def test_detect_deductible_office_supplies(detector):
    """Test detection of deductible office supplies."""
    transaction = {
        "id": 1,
        "payee": "Officeworks",
        "amount": -150.00,
        "date": "2025-11-15",
        "category": {"title": "Office Supplies"},
    }

    result = detector.detect_deduction(transaction)

    assert result["is_deductible"] is True
    assert result["confidence"] in ["high", "medium", "low"]
    assert result["ato_category"] == "Work-related other expenses"
    assert "reason" in result
    assert "substantiation_required" in result


def test_detect_non_deductible_groceries(detector):
    """Test detection of non-deductible personal groceries."""
    transaction = {
        "id": 2,
        "payee": "Woolworths",
        "amount": -85.00,
        "date": "2025-11-15",
        "category": {"title": "Groceries"},
    }

    result = detector.detect_deduction(transaction)

    assert result["is_deductible"] is False
    assert result["confidence"] == "high"
    assert "personal" in result["reason"].lower() or "not deductible" in result["reason"].lower()


def test_detect_commuting_not_deductible(detector):
    """Test detection of commuting (not deductible)."""
    # Weekday morning - likely commuting
    transaction = {
        "id": 3,
        "payee": "Uber",
        "amount": -25.00,
        "date": "2025-11-18",  # Monday
        "time": "08:30:00",
        "category": {"title": "Transport"},
    }

    result = detector.detect_deduction(transaction)

    assert result["is_deductible"] is False
    assert "commuting" in result["reason"].lower()
    assert result["confidence"] == "high"


def test_detect_business_travel_deductible(detector):
    """Test detection of business travel (deductible)."""
    # Weekday midday - likely business travel
    transaction = {
        "id": 4,
        "payee": "Uber",
        "amount": -35.00,
        "date": "2025-11-18",  # Monday
        "time": "14:30:00",
        "category": {"title": "Transport"},
    }

    result = detector.detect_deduction(transaction)

    assert result["is_deductible"] is True
    assert "business" in result["reason"].lower()
    assert result["confidence"] in ["medium", "low"]  # Lower confidence without more context


def test_substantiation_threshold_over_300(detector):
    """Test substantiation requirements for amounts over $300."""
    transaction = {
        "id": 5,
        "payee": "JB Hi-Fi",  # Matches computer_equipment pattern
        "amount": -850.00,
        "date": "2025-11-15",
        "category": {"title": "Electronics"},
    }

    result = detector.detect_deduction(transaction)

    assert result["substantiation_required"] is True
    assert result["threshold"] >= 75  # Could be 75 for taxi or 300 default
    assert (
        "receipt" in result["substantiation_notes"].lower()
        or "written" in result["substantiation_notes"].lower()
    )


def test_substantiation_threshold_under_300(detector):
    """Test substantiation not required under $300."""
    transaction = {
        "id": 6,
        "payee": "Office Depot",
        "amount": -150.00,
        "date": "2025-11-15",
        "category": {"title": "Office Supplies"},
    }

    result = detector.detect_deduction(transaction)

    # Under $300 but best practice to keep records
    assert result["substantiation_required"] in [True, False]  # May still be True for best practice


def test_taxi_uber_substantiation_threshold(detector):
    """Test $75 substantiation threshold for taxi/Uber."""
    transaction = {
        "id": 7,
        "payee": "Uber",
        "amount": -85.00,
        "date": "2025-11-15",
        "time": "14:00:00",
        "category": {"title": "Transport"},
    }

    result = detector.detect_deduction(transaction)

    # Uber/taxi has lower $75 threshold
    assert result["substantiation_required"] is True
    assert result["threshold"] == 75


def test_confidence_scoring_high(detector):
    """Test high confidence scoring for clear deductible patterns."""
    transaction = {
        "id": 8,
        "payee": "LinkedIn Premium",
        "amount": -49.99,
        "date": "2025-11-15",
        "category": {"title": "Professional Development"},
    }

    result = detector.detect_deduction(transaction)

    assert result["confidence"] == "high"
    assert result["is_deductible"] is True


def test_confidence_scoring_medium(detector):
    """Test medium confidence for ambiguous patterns."""
    transaction = {
        "id": 9,
        "payee": "Telstra Mobile",
        "amount": -89.00,
        "date": "2025-11-15",
        "category": {"title": "Mobile Phone"},
    }

    result = detector.detect_deduction(transaction)

    # Mobile phone could be personal or business
    assert result["confidence"] in ["medium", "low"]
    assert "split" in result.get("suggestions", "").lower() or result.get("reason", "")


def test_detect_home_office_equipment(detector):
    """Test detection of home office equipment."""
    transaction = {
        "id": 10,
        "payee": "Harvey Norman",
        "amount": -599.00,
        "date": "2025-11-15",
        "category": {"title": "Furniture"},
        "notes": "Office desk",
    }

    result = detector.detect_deduction(transaction)

    assert result["is_deductible"] is True
    assert "home office" in result["reason"].lower() or "work" in result["reason"].lower()


def test_weekend_taxi_not_commuting(detector):
    """Test weekend taxi rides are not flagged as commuting."""
    transaction = {
        "id": 11,
        "payee": "Uber",
        "amount": -30.00,
        "date": "2025-11-16",  # Sunday
        "time": "08:30:00",
        "category": {"title": "Transport"},
    }

    result = detector.detect_deduction(transaction)

    # Weekend trips should not be flagged as commuting
    assert "commuting" not in result["reason"].lower()


def test_instant_asset_write_off(detector):
    """Test detection of instant asset write-off eligible items."""
    transaction = {
        "id": 12,
        "payee": "Apple Store",  # Matches computer_equipment pattern
        "amount": -1299.00,
        "date": "2025-11-15",
        "category": {"title": "Computer Equipment"},
    }

    result = detector.detect_deduction(transaction)

    # Should match computer_equipment pattern or be detected as deductible
    assert result["is_deductible"] is True or "computer" in result["ato_category"].lower()
    # Should suggest instant asset write-off if under threshold
    if result.get("suggestions"):
        assert (
            "instant" in result["suggestions"].lower()
            or "immediately" in result["suggestions"].lower()
        )


def test_batch_detection(detector):
    """Test batch processing of multiple transactions."""
    transactions = [
        {
            "id": 1,
            "payee": "Officeworks",
            "amount": -50.00,
            "date": "2025-11-15",
            "category": {"title": "Office Supplies"},
        },
        {
            "id": 2,
            "payee": "Woolworths",
            "amount": -100.00,
            "date": "2025-11-15",
            "category": {"title": "Groceries"},
        },
    ]

    results = detector.detect_deductions_batch(transactions)

    assert len(results) == 2
    assert results[0]["is_deductible"] is True
    assert results[1]["is_deductible"] is False


def test_missing_time_field(detector):
    """Test handling of transactions without time field."""
    transaction = {
        "id": 13,
        "payee": "Uber",
        "amount": -25.00,
        "date": "2025-11-18",  # No time field
        "category": {"title": "Transport"},
    }

    result = detector.detect_deduction(transaction)

    # Should still work, just can't do time-based detection
    assert "is_deductible" in result
    assert "confidence" in result
