"""Tests for BAS preparation (Level 3 tax intelligence)."""

import pytest
from datetime import date
from scripts.tax.bas_preparation import generate_bas_worksheet


class TestBASPreparation:
    """Test suite for BAS worksheet generation."""

    def test_generate_bas_basic_structure(self):
        """Test basic BAS worksheet structure is returned."""
        transactions = []
        start_date = "2024-07-01"
        end_date = "2024-09-30"

        result = generate_bas_worksheet(transactions, start_date, end_date)

        # Check required fields exist
        assert "period" in result
        assert "G1_total_sales" in result
        assert "G10_capital_purchases" in result
        assert "G11_non_capital_purchases" in result
        assert "1A_gst_on_sales" in result
        assert "1B_gst_on_purchases" in result
        assert "1C_net_gst" in result
        assert "summary" in result
        assert "disclaimer" in result

    def test_bas_gst_on_sales(self):
        """Test GST calculation on sales (G1 and 1A)."""
        transactions = [
            {
                "id": 1,
                "date": "2024-07-15",
                "amount": 1100.0,  # GST-inclusive sale
                "payee": "Customer A",
                "category": {"title": "Business Income"},
                "is_transfer": False,
            },
            {
                "id": 2,
                "date": "2024-08-20",
                "amount": 2200.0,  # GST-inclusive sale
                "payee": "Customer B",
                "category": {"title": "Business Income"},
                "is_transfer": False,
            },
        ]

        result = generate_bas_worksheet(transactions, "2024-07-01", "2024-09-30")

        # G1: Total sales = 3300.00
        assert result["G1_total_sales"] == 3300.0

        # 1A: GST on sales = 1/11 of 3300 = 300.00
        assert result["1A_gst_on_sales"] == 300.0

    def test_bas_capital_purchases(self):
        """Test capital purchases classification (G10)."""
        transactions = [
            {
                "id": 1,
                "date": "2024-07-15",
                "amount": -11000.0,  # $10k + GST = capital
                "payee": "Equipment Supplier",
                "category": {"title": "Office Equipment"},
                "is_transfer": False,
            },
            {
                "id": 2,
                "date": "2024-08-20",
                "amount": -550.0,  # $500 + GST = non-capital
                "payee": "Office Supplies Store",
                "category": {"title": "Office Supplies"},
                "is_transfer": False,
            },
        ]

        result = generate_bas_worksheet(transactions, "2024-07-01", "2024-09-30")

        # G10: Capital purchases >= $1000 (GST-exclusive)
        # $11000 / 1.1 = $10000 (capital)
        assert result["G10_capital_purchases"] == 11000.0

        # G11: Non-capital purchases
        # $550 / 1.1 = $500 (non-capital)
        assert result["G11_non_capital_purchases"] == 550.0

    def test_bas_gst_on_purchases(self):
        """Test GST calculation on purchases (1B)."""
        transactions = [
            {
                "id": 1,
                "date": "2024-07-15",
                "amount": -1100.0,  # GST-inclusive purchase
                "payee": "Supplier",
                "category": {"title": "Office Supplies"},
                "is_transfer": False,
            },
        ]

        result = generate_bas_worksheet(transactions, "2024-07-01", "2024-09-30")

        # 1B: GST on purchases = 1/11 of 1100 = 100.00
        assert result["1B_gst_on_purchases"] == 100.0

    def test_bas_net_gst_calculation(self):
        """Test net GST calculation (1C = 1A - 1B)."""
        transactions = [
            # Sales
            {
                "id": 1,
                "date": "2024-07-15",
                "amount": 2200.0,  # Sale
                "payee": "Customer",
                "category": {"title": "Business Income"},
                "is_transfer": False,
            },
            # Purchases
            {
                "id": 2,
                "date": "2024-07-20",
                "amount": -1100.0,  # Purchase
                "payee": "Supplier",
                "category": {"title": "Office Supplies"},
                "is_transfer": False,
            },
        ]

        result = generate_bas_worksheet(transactions, "2024-07-01", "2024-09-30")

        # 1A: GST on sales = 2200 / 11 = 200.00
        assert result["1A_gst_on_sales"] == 200.0

        # 1B: GST on purchases = 1100 / 11 = 100.00
        assert result["1B_gst_on_purchases"] == 100.0

        # 1C: Net GST = 1A - 1B = 200 - 100 = 100.00
        assert result["1C_net_gst"] == 100.0

    def test_bas_excludes_transfers(self):
        """Test that transfers are excluded from BAS."""
        transactions = [
            {
                "id": 1,
                "date": "2024-07-15",
                "amount": -1000.0,
                "payee": "Transfer",
                "category": {"title": "Transfer"},
                "is_transfer": True,
            },
            {
                "id": 2,
                "date": "2024-07-20",
                "amount": -1100.0,
                "payee": "Supplier",
                "category": {"title": "Office Supplies"},
                "is_transfer": False,
            },
        ]

        result = generate_bas_worksheet(transactions, "2024-07-01", "2024-09-30")

        # Only the non-transfer purchase should be counted
        assert result["G11_non_capital_purchases"] == 1100.0
        assert result["1B_gst_on_purchases"] == 100.0

    def test_bas_excludes_gst_free_categories(self):
        """Test that GST-free categories are excluded."""
        transactions = [
            # GST-free: wages
            {
                "id": 1,
                "date": "2024-07-15",
                "amount": -5000.0,
                "payee": "Employee",
                "category": {"title": "Wages & Salaries"},
                "is_transfer": False,
            },
            # GST-free: bank fees
            {
                "id": 2,
                "date": "2024-07-20",
                "amount": -50.0,
                "payee": "Bank",
                "category": {"title": "Bank Fees"},
                "is_transfer": False,
            },
            # GST-applicable: office supplies
            {
                "id": 3,
                "date": "2024-07-25",
                "amount": -1100.0,
                "payee": "Supplier",
                "category": {"title": "Office Supplies"},
                "is_transfer": False,
            },
        ]

        result = generate_bas_worksheet(transactions, "2024-07-01", "2024-09-30")

        # Only office supplies should have GST
        assert result["G11_non_capital_purchases"] == 1100.0
        assert result["1B_gst_on_purchases"] == 100.0

    def test_bas_date_filtering(self):
        """Test transactions are filtered by date range."""
        transactions = [
            {
                "id": 1,
                "date": "2024-06-30",  # Before period
                "amount": -1100.0,
                "payee": "Supplier",
                "category": {"title": "Office Supplies"},
                "is_transfer": False,
            },
            {
                "id": 2,
                "date": "2024-07-15",  # In period
                "amount": -1100.0,
                "payee": "Supplier",
                "category": {"title": "Office Supplies"},
                "is_transfer": False,
            },
            {
                "id": 3,
                "date": "2024-10-01",  # After period
                "amount": -1100.0,
                "payee": "Supplier",
                "category": {"title": "Office Supplies"},
                "is_transfer": False,
            },
        ]

        result = generate_bas_worksheet(transactions, "2024-07-01", "2024-09-30")

        # Only transaction 2 should be included
        assert result["G11_non_capital_purchases"] == 1100.0
        assert result["1B_gst_on_purchases"] == 100.0

    def test_bas_summary_section(self):
        """Test summary section contains expected fields."""
        transactions = [
            {
                "id": 1,
                "date": "2024-07-15",
                "amount": 1100.0,  # Sale
                "payee": "Customer",
                "category": {"title": "Business Income"},
                "is_transfer": False,
            },
            {
                "id": 2,
                "date": "2024-07-20",
                "amount": -1100.0,  # Purchase
                "payee": "Supplier",
                "category": {"title": "Office Supplies"},
                "is_transfer": False,
            },
        ]

        result = generate_bas_worksheet(transactions, "2024-07-01", "2024-09-30")

        summary = result["summary"]
        assert "total_transactions" in summary
        assert "sales_count" in summary
        assert "purchase_count" in summary
        assert "capital_purchase_count" in summary
        assert "non_capital_purchase_count" in summary

        assert summary["total_transactions"] == 2
        assert summary["sales_count"] == 1
        assert summary["purchase_count"] == 1

    def test_bas_disclaimer_present(self):
        """Test Level 3 tax disclaimer is included."""
        transactions = []
        result = generate_bas_worksheet(transactions, "2024-07-01", "2024-09-30")

        disclaimer = result["disclaimer"]
        assert "registered tax agent" in disclaimer.lower()
        assert "level 3" in disclaimer.lower() or "full compliance" in disclaimer.lower()

    def test_bas_empty_transactions(self):
        """Test BAS generation with no transactions."""
        transactions = []
        result = generate_bas_worksheet(transactions, "2024-07-01", "2024-09-30")

        assert result["G1_total_sales"] == 0.0
        assert result["G10_capital_purchases"] == 0.0
        assert result["G11_non_capital_purchases"] == 0.0
        assert result["1A_gst_on_sales"] == 0.0
        assert result["1B_gst_on_purchases"] == 0.0
        assert result["1C_net_gst"] == 0.0

    def test_bas_period_formatting(self):
        """Test period information is correctly formatted."""
        transactions = []
        result = generate_bas_worksheet(transactions, "2024-07-01", "2024-09-30")

        period = result["period"]
        assert "start_date" in period
        assert "end_date" in period
        assert period["start_date"] == "2024-07-01"
        assert period["end_date"] == "2024-09-30"

    def test_bas_rounding(self):
        """Test all amounts are rounded to 2 decimal places."""
        transactions = [
            {
                "id": 1,
                "date": "2024-07-15",
                "amount": 1103.33,  # Odd amount
                "payee": "Customer",
                "category": {"title": "Business Income"},
                "is_transfer": False,
            },
        ]

        result = generate_bas_worksheet(transactions, "2024-07-01", "2024-09-30")

        # All amounts should be rounded to 2 decimal places
        assert isinstance(result["G1_total_sales"], float)
        assert isinstance(result["1A_gst_on_sales"], float)
        assert round(result["1A_gst_on_sales"], 2) == result["1A_gst_on_sales"]

    def test_bas_negative_net_gst(self):
        """Test net GST can be negative (refund due)."""
        transactions = [
            # Small sale
            {
                "id": 1,
                "date": "2024-07-15",
                "amount": 1100.0,
                "payee": "Customer",
                "category": {"title": "Business Income"},
                "is_transfer": False,
            },
            # Large purchase
            {
                "id": 2,
                "date": "2024-07-20",
                "amount": -5500.0,
                "payee": "Supplier",
                "category": {"title": "Office Equipment"},
                "is_transfer": False,
            },
        ]

        result = generate_bas_worksheet(transactions, "2024-07-01", "2024-09-30")

        # 1A: 1100 / 11 = 100
        # 1B: 5500 / 11 = 500
        # 1C: 100 - 500 = -400 (refund)
        assert result["1A_gst_on_sales"] == 100.0
        assert result["1B_gst_on_purchases"] == 500.0
        assert result["1C_net_gst"] == -400.0
