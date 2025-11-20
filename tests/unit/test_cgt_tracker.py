"""Tests for Capital Gains Tax tracking (Level 2 tax intelligence)."""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from scripts.tax.cgt_tracker import CGTTracker, Asset, CGTEvent, AssetType


@pytest.fixture
def tracker():
    """Create CGTTracker instance for testing."""
    return CGTTracker()


def test_asset_creation():
    """Test Asset dataclass creation."""
    asset = Asset(
        asset_id="AAPL-001",
        asset_type=AssetType.SHARES,
        name="Apple Inc.",
        quantity=Decimal("10"),
        purchase_date=date(2024, 1, 15),
        purchase_price=Decimal("150.00"),
        fees=Decimal("9.95"),
    )

    assert asset.asset_id == "AAPL-001"
    assert asset.asset_type == AssetType.SHARES
    assert asset.name == "Apple Inc."
    assert asset.quantity == Decimal("10")
    assert asset.purchase_date == date(2024, 1, 15)
    assert asset.purchase_price == Decimal("150.00")
    assert asset.fees == Decimal("9.95")
    assert asset.cost_base == Decimal("1509.95")  # (150 * 10) + 9.95


def test_cgt_event_creation():
    """Test CGTEvent dataclass creation."""
    event = CGTEvent(
        event_id="SALE-001",
        asset_id="AAPL-001",
        event_type="sale",
        event_date=date(2025, 6, 15),
        quantity=Decimal("5"),
        sale_price=Decimal("180.00"),
        fees=Decimal("9.95"),
        holding_period_days=517,
        discount_eligible=True,
        capital_gain=Decimal("140.05"),
    )

    assert event.event_id == "SALE-001"
    assert event.asset_id == "AAPL-001"
    assert event.event_type == "sale"
    assert event.quantity == Decimal("5")
    assert event.discount_eligible is True
    assert event.holding_period_days == 517


def test_track_asset_purchase(tracker):
    """Test tracking an asset purchase."""
    asset = tracker.track_purchase(
        asset_type=AssetType.SHARES,
        name="BHP Group",
        quantity=Decimal("100"),
        purchase_date=date(2024, 3, 1),
        purchase_price=Decimal("45.50"),
        fees=Decimal("19.95"),
    )

    assert asset.asset_id is not None
    assert asset.asset_type == AssetType.SHARES
    assert asset.name == "BHP Group"
    assert asset.quantity == Decimal("100")
    assert asset.cost_base == Decimal("4569.95")  # (45.50 * 100) + 19.95
    assert len(tracker.get_all_assets()) == 1


def test_track_multiple_purchases_same_asset(tracker):
    """Test tracking multiple purchases of the same asset (different parcels)."""
    # First purchase
    asset1 = tracker.track_purchase(
        asset_type=AssetType.SHARES,
        name="CBA",
        quantity=Decimal("50"),
        purchase_date=date(2024, 1, 15),
        purchase_price=Decimal("100.00"),
        fees=Decimal("9.95"),
    )

    # Second purchase (different parcel)
    asset2 = tracker.track_purchase(
        asset_type=AssetType.SHARES,
        name="CBA",
        quantity=Decimal("30"),
        purchase_date=date(2024, 6, 20),
        purchase_price=Decimal("110.00"),
        fees=Decimal("9.95"),
    )

    assets = tracker.get_all_assets()
    assert len(assets) == 2
    assert asset1.asset_id != asset2.asset_id  # Different parcels
    assert assets[0].purchase_date < assets[1].purchase_date  # Ordered by date


def test_track_sale_within_12_months_no_discount(tracker):
    """Test sale within 12 months (no CGT discount)."""
    # Purchase
    tracker.track_purchase(
        asset_type=AssetType.SHARES,
        name="WES",
        quantity=Decimal("100"),
        purchase_date=date(2024, 6, 1),
        purchase_price=Decimal("50.00"),
        fees=Decimal("19.95"),
    )

    # Sale after 8 months
    event = tracker.track_sale(
        asset_type=AssetType.SHARES,
        name="WES",
        quantity=Decimal("100"),
        sale_date=date(2025, 2, 1),  # 8 months later
        sale_price=Decimal("60.00"),
        fees=Decimal("19.95"),
    )

    assert event.holding_period_days < 365
    assert event.discount_eligible is False
    # Capital gain: (60*100 - 19.95) - (50*100 + 19.95) = 5980.05 - 5019.95
    assert event.capital_gain == Decimal("960.10")


def test_track_sale_over_12_months_with_discount(tracker):
    """Test sale after 12 months (50% CGT discount eligible)."""
    # Purchase
    tracker.track_purchase(
        asset_type=AssetType.SHARES,
        name="CSL",
        quantity=Decimal("50"),
        purchase_date=date(2023, 1, 1),
        purchase_price=Decimal("200.00"),
        fees=Decimal("19.95"),
    )

    # Sale after 18 months
    event = tracker.track_sale(
        asset_type=AssetType.SHARES,
        name="CSL",
        quantity=Decimal("50"),
        sale_date=date(2024, 7, 1),  # 18 months later
        sale_price=Decimal("250.00"),
        fees=Decimal("19.95"),
    )

    assert event.holding_period_days > 365
    assert event.discount_eligible is True
    # Capital gain: (250*50 - 19.95) - (200*50 + 19.95) = 2460.10
    assert event.capital_gain == Decimal("2460.10")


def test_fifo_matching_partial_sale(tracker):
    """Test FIFO matching for partial sale across multiple parcels."""
    # First purchase (100 shares)
    tracker.track_purchase(
        asset_type=AssetType.SHARES,
        name="ANZ",
        quantity=Decimal("100"),
        purchase_date=date(2023, 1, 1),
        purchase_price=Decimal("25.00"),
        fees=Decimal("9.95"),
    )

    # Second purchase (100 shares)
    tracker.track_purchase(
        asset_type=AssetType.SHARES,
        name="ANZ",
        quantity=Decimal("100"),
        purchase_date=date(2024, 1, 1),
        purchase_price=Decimal("30.00"),
        fees=Decimal("9.95"),
    )

    # Sell 150 shares (should match FIFO: all of first parcel + 50 from second)
    events = tracker.track_sale(
        asset_type=AssetType.SHARES,
        name="ANZ",
        quantity=Decimal("150"),
        sale_date=date(2024, 6, 1),
        sale_price=Decimal("35.00"),
        fees=Decimal("14.95"),
    )

    # Should create 2 CGT events (one per parcel)
    assert len(events) == 2

    # First event: 100 shares from first parcel (held > 12 months)
    assert events[0].quantity == Decimal("100")
    assert events[0].discount_eligible is True

    # Second event: 50 shares from second parcel (held < 12 months)
    assert events[1].quantity == Decimal("50")
    assert events[1].discount_eligible is False


def test_get_remaining_holdings(tracker):
    """Test getting remaining holdings for an asset."""
    # Purchase 200 shares
    tracker.track_purchase(
        asset_type=AssetType.SHARES,
        name="WOW",
        quantity=Decimal("200"),
        purchase_date=date(2024, 1, 1),
        purchase_price=Decimal("35.00"),
        fees=Decimal("19.95"),
    )

    # Sell 80 shares
    tracker.track_sale(
        asset_type=AssetType.SHARES,
        name="WOW",
        quantity=Decimal("80"),
        sale_date=date(2024, 6, 1),
        sale_price=Decimal("40.00"),
        fees=Decimal("9.95"),
    )

    holdings = tracker.get_holdings(AssetType.SHARES, "WOW")
    assert holdings["total_quantity"] == Decimal("120")  # 200 - 80
    assert holdings["total_cost_base"] > 0


def test_track_crypto_purchase_and_sale(tracker):
    """Test tracking cryptocurrency purchases and sales."""
    # Purchase Bitcoin
    tracker.track_purchase(
        asset_type=AssetType.CRYPTO,
        name="Bitcoin",
        quantity=Decimal("0.5"),
        purchase_date=date(2023, 1, 1),
        purchase_price=Decimal("30000.00"),
        fees=Decimal("150.00"),
    )

    # Sale after 18 months
    event = tracker.track_sale(
        asset_type=AssetType.CRYPTO,
        name="Bitcoin",
        quantity=Decimal("0.5"),
        sale_date=date(2024, 7, 1),
        sale_price=Decimal("60000.00"),
        fees=Decimal("300.00"),
    )

    assert event.discount_eligible is True
    assert event.holding_period_days > 365
    # Capital gain: (60000*0.5 - 300) - (30000*0.5 + 150) = 29700 - 15150 = 14550
    assert event.capital_gain == Decimal("14550.00")


def test_track_property_purchase_and_sale(tracker):
    """Test tracking property purchases and sales."""
    # Purchase investment property
    tracker.track_purchase(
        asset_type=AssetType.PROPERTY,
        name="123 Main St, Sydney",
        quantity=Decimal("1"),
        purchase_date=date(2020, 1, 1),
        purchase_price=Decimal("800000.00"),
        fees=Decimal("32000.00"),  # Stamp duty, legal fees, etc.
    )

    # Sale after 4 years
    event = tracker.track_sale(
        asset_type=AssetType.PROPERTY,
        name="123 Main St, Sydney",
        quantity=Decimal("1"),
        sale_date=date(2024, 6, 1),
        sale_price=Decimal("1100000.00"),
        fees=Decimal("33000.00"),  # Agent commission, legal fees
    )

    assert event.discount_eligible is True
    assert event.holding_period_days > 365
    # Capital gain: (1100000*1 - 33000) - (800000*1 + 32000) = 235000
    assert event.capital_gain == Decimal("235000.00")


def test_calculate_holding_period(tracker):
    """Test holding period calculation."""
    purchase_date = date(2024, 1, 1)
    sale_date = date(2024, 7, 1)

    days = tracker._calculate_holding_period(purchase_date, sale_date)

    assert days == 182  # Approximately 6 months


def test_get_cgt_events_for_financial_year(tracker):
    """Test retrieving CGT events for a specific financial year."""
    # Purchase and sale in FY 2023-24
    tracker.track_purchase(
        asset_type=AssetType.SHARES,
        name="NAB",
        quantity=Decimal("100"),
        purchase_date=date(2023, 8, 1),
        purchase_price=Decimal("28.00"),
        fees=Decimal("9.95"),
    )

    tracker.track_sale(
        asset_type=AssetType.SHARES,
        name="NAB",
        quantity=Decimal("100"),
        sale_date=date(2024, 5, 15),  # Within FY 2023-24
        sale_price=Decimal("32.00"),
        fees=Decimal("9.95"),
    )

    # Purchase and sale in FY 2024-25
    tracker.track_purchase(
        asset_type=AssetType.SHARES,
        name="WBC",
        quantity=Decimal("50"),
        purchase_date=date(2024, 7, 1),
        purchase_price=Decimal("25.00"),
        fees=Decimal("9.95"),
    )

    tracker.track_sale(
        asset_type=AssetType.SHARES,
        name="WBC",
        quantity=Decimal("50"),
        sale_date=date(2024, 12, 1),  # Within FY 2024-25
        sale_price=Decimal("28.00"),
        fees=Decimal("9.95"),
    )

    # Get events for FY 2023-24 (July 1, 2023 to June 30, 2024)
    events_2024 = tracker.get_events_for_financial_year(2024)
    assert len(events_2024) == 1

    # Get events for FY 2024-25 (July 1, 2024 to June 30, 2025)
    events_2025 = tracker.get_events_for_financial_year(2025)
    assert len(events_2025) == 1


def test_calculate_total_capital_gains(tracker):
    """Test calculating total capital gains for a period."""
    # Multiple sales
    tracker.track_purchase(
        asset_type=AssetType.SHARES,
        name="TLS",
        quantity=Decimal("100"),
        purchase_date=date(2023, 1, 1),
        purchase_price=Decimal("3.50"),
        fees=Decimal("9.95"),
    )

    tracker.track_sale(
        asset_type=AssetType.SHARES,
        name="TLS",
        quantity=Decimal("100"),
        sale_date=date(2024, 6, 1),
        sale_price=Decimal("4.00"),
        fees=Decimal("9.95"),
    )

    tracker.track_purchase(
        asset_type=AssetType.CRYPTO,
        name="Ethereum",
        quantity=Decimal("2"),
        purchase_date=date(2023, 6, 1),
        purchase_price=Decimal("2000.00"),
        fees=Decimal("40.00"),
    )

    tracker.track_sale(
        asset_type=AssetType.CRYPTO,
        name="Ethereum",
        quantity=Decimal("2"),
        sale_date=date(2024, 6, 15),
        sale_price=Decimal("3000.00"),
        fees=Decimal("60.00"),
    )

    total = tracker.calculate_total_capital_gains(2024)  # FY 2023-24 (sales in June 2024)
    assert total["total_gain"] > 0
    assert total["discount_eligible_gain"] > 0
    assert total["non_discount_gain"] >= 0


def test_error_sale_without_purchase(tracker):
    """Test error when trying to sell asset that wasn't purchased."""
    with pytest.raises(ValueError, match="No holdings found"):
        tracker.track_sale(
            asset_type=AssetType.SHARES,
            name="XYZ",
            quantity=Decimal("100"),
            sale_date=date(2024, 6, 1),
            sale_price=Decimal("50.00"),
            fees=Decimal("9.95"),
        )


def test_error_insufficient_quantity(tracker):
    """Test error when trying to sell more than owned."""
    tracker.track_purchase(
        asset_type=AssetType.SHARES,
        name="ABC",
        quantity=Decimal("50"),
        purchase_date=date(2024, 1, 1),
        purchase_price=Decimal("10.00"),
        fees=Decimal("9.95"),
    )

    with pytest.raises(ValueError, match="Insufficient quantity"):
        tracker.track_sale(
            asset_type=AssetType.SHARES,
            name="ABC",
            quantity=Decimal("100"),  # Trying to sell more than owned
            sale_date=date(2024, 6, 1),
            sale_price=Decimal("15.00"),
            fees=Decimal("9.95"),
        )


def test_cost_base_calculation():
    """Test cost base includes purchase price plus fees."""
    asset = Asset(
        asset_id="TEST-001",
        asset_type=AssetType.SHARES,
        name="Test Co",
        quantity=Decimal("100"),
        purchase_date=date(2024, 1, 1),
        purchase_price=Decimal("10.00"),
        fees=Decimal("50.00"),
    )

    # Cost base = (quantity * price) + fees
    expected_cost_base = (Decimal("100") * Decimal("10.00")) + Decimal("50.00")
    assert asset.cost_base == expected_cost_base


def test_capital_gain_calculation():
    """Test capital gain calculation: (sale proceeds - fees) - cost base."""
    # This is implicitly tested in other tests, but explicitly here
    tracker = CGTTracker()

    tracker.track_purchase(
        asset_type=AssetType.SHARES,
        name="TEST",
        quantity=Decimal("100"),
        purchase_date=date(2024, 1, 1),
        purchase_price=Decimal("10.00"),  # $1000 total
        fees=Decimal("20.00"),  # Cost base: $1020
    )

    event = tracker.track_sale(
        asset_type=AssetType.SHARES,
        name="TEST",
        quantity=Decimal("100"),
        sale_date=date(2024, 6, 1),
        sale_price=Decimal("15.00"),  # $1500 total
        fees=Decimal("30.00"),  # Sale proceeds: $1470
    )

    # Capital gain: $1470 - $1020 = $450
    assert event.capital_gain == Decimal("450.00")


def test_cost_base_tracking_after_partial_sale(tracker):
    """Test that cost base is correctly reduced after partial sales."""
    # Purchase 200 shares @ $35, fees $19.95
    # Total cost: 200 * 35 + 19.95 = 7019.95
    tracker.track_purchase(
        asset_type=AssetType.SHARES,
        name="TEST",
        quantity=Decimal("200"),
        purchase_date=date(2024, 1, 1),
        purchase_price=Decimal("35.00"),
        fees=Decimal("19.95"),
    )

    # Sell 80 shares (40% of holding)
    tracker.track_sale(
        asset_type=AssetType.SHARES,
        name="TEST",
        quantity=Decimal("80"),
        sale_date=date(2024, 6, 1),
        sale_price=Decimal("40.00"),
        fees=Decimal("9.95"),
    )

    holdings = tracker.get_holdings(AssetType.SHARES, "TEST")

    # Sold 40%, remaining 60%
    expected_cost_base = Decimal("7019.95") * Decimal("0.6")

    assert holdings["total_quantity"] == Decimal("120")
    assert holdings["total_cost_base"] == expected_cost_base  # Should be $4,211.97
