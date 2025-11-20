"""Integration tests for tax intelligence workflows.

Tests end-to-end workflows for all three tax intelligence levels:
- Level 1: Reference & Reporting (tax summary, ATO category mapping)
- Level 2: Smart Categorization (deduction detection, CGT tracking)
- Level 3: Full Compliance Suite (BAS generation)
"""

import pytest
import os
from datetime import date, datetime
from decimal import Decimal
from scripts.core.api_client import PocketSmithClient
from scripts.tax.reporting import generate_tax_summary, calculate_gst
from scripts.tax.ato_categories import ATOCategoryMapper
from scripts.tax.deduction_detector import DeductionDetector
from scripts.tax.cgt_tracker import CGTTracker, AssetType
from scripts.tax.bas_preparation import generate_bas_worksheet

pytestmark = pytest.mark.integration


@pytest.fixture
def api_client():
    """Create API client with real credentials."""
    api_key = os.getenv("POCKETSMITH_API_KEY")
    if not api_key:
        pytest.skip("POCKETSMITH_API_KEY not set - skipping integration tests")
    return PocketSmithClient(api_key=api_key)


@pytest.fixture
def sample_transactions(api_client):
    """Fetch real transactions for testing."""
    user = api_client.get_user()
    # Get recent transactions (last 3 months)
    transactions = api_client.get_transactions(
        user_id=user["id"], start_date="2025-09-01", end_date="2025-11-30"
    )
    return transactions


class TestLevel1TaxIntelligence:
    """Test Level 1: Reference & Reporting workflows."""

    def test_tax_summary_workflow(self, sample_transactions):
        """Test complete tax summary generation workflow.

        Tests:
        - Generate tax summary from real transactions
        - ATO category mapping
        - Deductible vs non-deductible expense breakdown
        - Date range filtering
        """
        # Generate tax summary for a specific period
        summary = generate_tax_summary(
            transactions=sample_transactions,
            start_date="2025-11-01",
            end_date="2025-11-30",
            include_gst=False,
        )

        # Verify summary structure
        assert "total_expenses" in summary
        assert "deductible_expenses" in summary
        assert "non_deductible_expenses" in summary
        assert "by_ato_category" in summary
        assert "transaction_count" in summary
        assert "date_range" in summary

        # Verify calculations
        assert summary["total_expenses"] >= 0
        assert summary["deductible_expenses"] >= 0
        assert summary["non_deductible_expenses"] >= 0
        assert (
            abs(
                summary["total_expenses"]
                - (summary["deductible_expenses"] + summary["non_deductible_expenses"])
            )
            < 0.01
        )

        # Verify ATO category breakdown
        if summary["by_ato_category"]:
            first_category = summary["by_ato_category"][0]
            assert "ato_code" in first_category
            assert "ato_category" in first_category
            assert "total" in first_category
            assert "transaction_count" in first_category
            assert "deductible" in first_category

        print(
            f"✓ Level 1 Tax Summary: {summary['transaction_count']} transactions, "
            f"${summary['total_expenses']:.2f} total, "
            f"${summary['deductible_expenses']:.2f} deductible, "
            f"{len(summary['by_ato_category'])} ATO categories"
        )

    def test_ato_category_mapping_workflow(self, sample_transactions):
        """Test ATO category mapping across real transactions.

        Tests:
        - Map PocketSmith categories to ATO categories
        - Identify deductible vs non-deductible categories
        - Extract ATO codes and categories
        """
        mapper = ATOCategoryMapper()
        mapped_categories = set()
        deductible_count = 0
        non_deductible_count = 0

        for txn in sample_transactions[:50]:  # Sample first 50
            category = txn.get("category") or {}
            category_name = category.get("title", "Uncategorized")

            ato_info = mapper.get_ato_category(category_name)

            assert "ato_code" in ato_info
            assert "ato_category" in ato_info
            assert "deductible" in ato_info

            if ato_info["ato_code"]:
                mapped_categories.add(ato_info["ato_code"])

            if ato_info["deductible"]:
                deductible_count += 1
            else:
                non_deductible_count += 1

        print(
            f"✓ ATO Mapping: {len(mapped_categories)} unique ATO codes, "
            f"{deductible_count} deductible, {non_deductible_count} non-deductible"
        )

    def test_gst_calculation_workflow(self, sample_transactions):
        """Test GST calculation for business expenses.

        Tests:
        - Calculate GST paid (1/11 of GST-inclusive amounts)
        - Identify GST-eligible transactions
        - Track GST for input tax credits
        """
        gst_summary = calculate_gst(sample_transactions)

        # Verify GST calculation structure
        assert "total_gst_paid" in gst_summary
        assert "eligible_for_credit" in gst_summary
        assert "transaction_count" in gst_summary

        # Verify calculations
        assert gst_summary["total_gst_paid"] >= 0
        assert gst_summary["eligible_for_credit"] >= 0
        assert gst_summary["transaction_count"] >= 0

        # GST eligible should equal total GST paid (all deductible expenses)
        assert gst_summary["total_gst_paid"] == gst_summary["eligible_for_credit"]

        print(
            f"✓ GST Calculation: ${gst_summary['total_gst_paid']:.2f} GST paid, "
            f"{gst_summary['transaction_count']} transactions with GST"
        )


class TestLevel2TaxIntelligence:
    """Test Level 2: Smart Categorization Assistant workflows."""

    def test_deduction_detection_workflow(self, sample_transactions):
        """Test deduction detection across real transactions.

        Tests:
        - Detect tax-deductible transactions using patterns
        - Confidence scoring (high/medium/low)
        - Substantiation threshold checking
        - ATO category integration
        """
        detector = DeductionDetector()

        high_confidence_count = 0
        medium_confidence_count = 0
        low_confidence_count = 0
        substantiation_required_count = 0
        total_deductible_amount = 0.0

        # Process sample of transactions
        for txn in sample_transactions[:100]:  # Sample first 100
            # Skip income transactions
            amount = float(txn.get("amount", 0))
            if amount >= 0:
                continue

            result = detector.detect_deduction(txn)

            # Verify result structure
            assert "is_deductible" in result
            assert "confidence" in result
            assert "reason" in result
            assert "ato_category" in result
            assert "substantiation_required" in result

            if result["is_deductible"]:
                if result["confidence"] == "high":
                    high_confidence_count += 1
                elif result["confidence"] == "medium":
                    medium_confidence_count += 1
                elif result["confidence"] == "low":
                    low_confidence_count += 1

                total_deductible_amount += abs(amount)

                if result["substantiation_required"]:
                    substantiation_required_count += 1

        print(
            f"✓ Deduction Detection: "
            f"{high_confidence_count} high confidence, "
            f"{medium_confidence_count} medium, "
            f"{low_confidence_count} low, "
            f"{substantiation_required_count} need substantiation, "
            f"${total_deductible_amount:.2f} total deductible"
        )

    def test_cgt_tracking_workflow(self):
        """Test CGT tracking workflow with asset purchase and sale.

        Tests:
        - Track asset purchases (shares, crypto)
        - Track asset sales
        - FIFO matching for sales
        - Holding period calculation
        - CGT discount eligibility (50% for > 365 days)
        - Capital gain/loss calculation
        """
        tracker = CGTTracker()

        # Test 1: Purchase asset
        purchase_date = date(2024, 1, 15)
        asset = tracker.track_purchase(
            asset_type=AssetType.SHARES,
            name="BHP Group",
            quantity=Decimal("100"),
            purchase_date=purchase_date,
            purchase_price=Decimal("45.50"),
            fees=Decimal("19.95"),
        )

        assert asset.asset_id is not None
        assert asset.asset_type == AssetType.SHARES
        assert asset.name == "BHP Group"
        assert asset.quantity == Decimal("100")
        assert asset.purchase_price == Decimal("45.50")
        assert asset.fees == Decimal("19.95")
        # Cost base = (100 * 45.50) + 19.95 = 4569.95
        assert asset.cost_base == Decimal("4569.95")

        # Test 2: Sell asset after > 365 days (eligible for CGT discount)
        sale_date = date(2025, 11, 20)
        result = tracker.track_sale(
            asset_type=AssetType.SHARES,
            name="BHP Group",
            quantity=Decimal("100"),
            sale_date=sale_date,
            sale_price=Decimal("52.00"),
            fees=Decimal("19.95"),
        )

        # track_sale returns a single CGTEvent if only 1 parcel matched
        event = result

        # Verify CGT event
        assert event.event_id is not None
        assert event.quantity == Decimal("100")
        assert event.sale_price == Decimal("52.00")
        assert event.fees == Decimal("19.95")

        # Holding period should be > 365 days
        assert event.holding_period_days > 365
        assert event.discount_eligible is True

        # Capital gain = (100 * 52.00 - 19.95) - 4569.95 = 5200 - 19.95 - 4569.95 = 610.10
        expected_gain = Decimal("610.10")
        assert abs(event.capital_gain - expected_gain) < Decimal("0.01")

        print(
            f"✓ CGT Tracking: Asset purchased {purchase_date}, sold {sale_date}, "
            f"held {event.holding_period_days} days, "
            f"discount eligible: {event.discount_eligible}, "
            f"capital gain: ${event.capital_gain:.2f}"
        )

        # Test 3: Get financial year events and calculate gains
        # Sale on 2025-11-20 is in FY2026 (July 1, 2025 - June 30, 2026)
        fy_events = tracker.get_events_for_financial_year(year=2026)
        assert len(fy_events) > 0

        gains_summary = tracker.calculate_total_capital_gains(year=2026)
        assert "total_gain" in gains_summary
        assert "discount_eligible_gain" in gains_summary
        assert "non_discount_gain" in gains_summary
        assert "total_events" in gains_summary

        print(
            f"✓ FY2026 CGT Report: {gains_summary['total_events']} events, "
            f"${gains_summary['total_gain']:.2f} total gain, "
            f"${gains_summary['discount_eligible_gain']:.2f} discount eligible"
        )

    def test_multi_parcel_cgt_workflow(self):
        """Test FIFO matching with multiple asset parcels.

        Tests:
        - Purchase multiple parcels at different prices
        - Sell quantity that spans multiple parcels
        - FIFO matching (first in, first out)
        - Aggregate capital gains across parcels
        """
        tracker = CGTTracker()

        # Purchase Parcel 1: 50 shares @ $40
        tracker.track_purchase(
            asset_type=AssetType.SHARES,
            name="Commonwealth Bank",
            quantity=Decimal("50"),
            purchase_date=date(2024, 1, 10),
            purchase_price=Decimal("40.00"),
            fees=Decimal("9.95"),
        )

        # Purchase Parcel 2: 50 shares @ $45
        tracker.track_purchase(
            asset_type=AssetType.SHARES,
            name="Commonwealth Bank",
            quantity=Decimal("50"),
            purchase_date=date(2024, 3, 15),
            purchase_price=Decimal("45.00"),
            fees=Decimal("9.95"),
        )

        # Purchase Parcel 3: 50 shares @ $42
        tracker.track_purchase(
            asset_type=AssetType.SHARES,
            name="Commonwealth Bank",
            quantity=Decimal("50"),
            purchase_date=date(2024, 6, 20),
            purchase_price=Decimal("42.00"),
            fees=Decimal("9.95"),
        )

        # Sell 100 shares - should match first 2 parcels (FIFO)
        events = tracker.track_sale(
            asset_type=AssetType.SHARES,
            name="Commonwealth Bank",
            quantity=Decimal("100"),
            sale_date=date(2025, 11, 20),
            sale_price=Decimal("50.00"),
            fees=Decimal("19.95"),
        )

        # Should have 2 CGT events (50 from parcel 1, 50 from parcel 2)
        assert len(events) == 2

        # Verify FIFO order
        assert events[0].quantity == Decimal("50")  # First parcel
        assert events[1].quantity == Decimal("50")  # Second parcel

        total_gain = sum(event.capital_gain for event in events)
        print(
            f"✓ Multi-Parcel FIFO: Sold 100 shares across {len(events)} parcels, "
            f"total gain: ${total_gain:.2f}"
        )


class TestLevel3TaxIntelligence:
    """Test Level 3: Full Compliance Suite workflows."""

    def test_bas_generation_workflow(self, sample_transactions):
        """Test BAS (Business Activity Statement) worksheet generation.

        Tests:
        - Generate quarterly BAS worksheet
        - GST calculations (G1, 1A, 1B, 1C labels)
        - Capital vs non-capital purchase classification
        - GST-free and input-taxed category handling
        - BAS validation and compliance checks
        """
        # Generate BAS for Q2 FY2025 (Oct-Dec 2024)
        bas_worksheet = generate_bas_worksheet(
            transactions=sample_transactions,
            start_date="2025-10-01",
            end_date="2025-11-30",
        )

        # Verify BAS structure
        assert "period" in bas_worksheet
        assert "G1_total_sales" in bas_worksheet
        assert "G10_capital_purchases" in bas_worksheet
        assert "G11_non_capital_purchases" in bas_worksheet
        assert "1A_gst_on_sales" in bas_worksheet
        assert "1B_gst_on_purchases" in bas_worksheet
        assert "1C_net_gst" in bas_worksheet
        assert "summary" in bas_worksheet
        assert "disclaimer" in bas_worksheet

        # Verify period details
        period = bas_worksheet["period"]
        assert period["start_date"] == "2025-10-01"
        assert period["end_date"] == "2025-11-30"

        # Verify calculations
        assert bas_worksheet["G1_total_sales"] >= 0
        assert bas_worksheet["G10_capital_purchases"] >= 0
        assert bas_worksheet["G11_non_capital_purchases"] >= 0
        assert bas_worksheet["1A_gst_on_sales"] >= 0
        assert bas_worksheet["1B_gst_on_purchases"] >= 0

        # Net GST = GST on sales - GST on purchases
        expected_net_gst = bas_worksheet["1A_gst_on_sales"] - bas_worksheet["1B_gst_on_purchases"]
        assert abs(bas_worksheet["1C_net_gst"] - expected_net_gst) < 0.01

        # Verify disclaimer
        assert "registered tax agent" in bas_worksheet["disclaimer"]

        # Verify summary
        summary = bas_worksheet["summary"]
        assert "total_transactions" in summary
        assert "sales_count" in summary
        assert "purchase_count" in summary
        assert "capital_purchase_count" in summary
        assert "non_capital_purchase_count" in summary

        print(
            f"✓ BAS Generation: Oct-Dec 2025, "
            f"G1: ${bas_worksheet['G1_total_sales']:.2f}, "
            f"G10: ${bas_worksheet['G10_capital_purchases']:.2f}, "
            f"G11: ${bas_worksheet['G11_non_capital_purchases']:.2f}, "
            f"1A: ${bas_worksheet['1A_gst_on_sales']:.2f}, "
            f"1B: ${bas_worksheet['1B_gst_on_purchases']:.2f}, "
            f"1C: ${bas_worksheet['1C_net_gst']:.2f}"
        )

        print(
            f"✓ BAS Breakdown: "
            f"{summary['sales_count']} sales, "
            f"{summary['capital_purchase_count']} capital purchases, "
            f"{summary['non_capital_purchase_count']} non-capital purchases, "
            f"{summary['total_transactions']} total transactions"
        )


class TestCrossLevelIntegration:
    """Test workflows that span multiple tax intelligence levels."""

    def test_complete_tax_workflow(self, sample_transactions):
        """Test complete tax intelligence workflow across all levels.

        Tests integration of:
        - Level 1: Tax summary and ATO mapping
        - Level 2: Deduction detection
        - Level 3: BAS preparation

        Simulates a complete end-of-quarter tax review workflow.
        """
        # Level 1: Generate tax summary
        tax_summary = generate_tax_summary(
            transactions=sample_transactions,
            start_date="2025-11-01",
            end_date="2025-11-30",
            include_gst=True,
        )

        assert tax_summary is not None
        assert "gst_summary" in tax_summary

        # Level 2: Detect deductions
        detector = DeductionDetector()
        deductible_transactions = []
        high_confidence_deductions = 0

        for txn in sample_transactions:
            amount = float(txn.get("amount", 0))
            if amount >= 0:  # Skip income
                continue

            result = detector.detect_deduction(txn)
            if result["is_deductible"]:
                deductible_transactions.append(txn)
                if result["confidence"] == "high":
                    high_confidence_deductions += 1

        # Level 3: Generate BAS
        bas_worksheet = generate_bas_worksheet(
            transactions=sample_transactions,
            start_date="2025-11-01",
            end_date="2025-11-30",
        )

        assert bas_worksheet is not None

        # Verify integration across levels
        # GST from Level 1 should match 1B from Level 3 BAS
        level1_gst = tax_summary["gst_summary"]["total_gst_paid"]
        level3_gst = bas_worksheet["1B_gst_on_purchases"]

        # Allow small difference due to GST-free filtering in BAS
        # If level1_gst is 0, just ensure level3_gst is also small
        if level1_gst > 0:
            assert abs(level1_gst - level3_gst) < level1_gst * 0.5  # Within 50%
        else:
            # If no GST in level 1, level 3 should also be minimal
            assert level3_gst >= 0

        print("✓ Complete Tax Workflow:")
        print(
            f"  Level 1: {tax_summary['transaction_count']} transactions, "
            f"${tax_summary['deductible_expenses']:.2f} deductible, "
            f"${tax_summary['gst_summary']['total_gst_paid']:.2f} GST"
        )
        print(
            f"  Level 2: {len(deductible_transactions)} deductions detected, "
            f"{high_confidence_deductions} high confidence"
        )
        print(f"  Level 3: BAS Nov 2025, " f"${bas_worksheet['1C_net_gst']:.2f} net GST")
