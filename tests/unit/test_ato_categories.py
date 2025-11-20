"""Tests for ATO category mappings."""

import pytest
from scripts.tax.ato_categories import ATOCategoryMapper


def test_get_ato_category_for_groceries():
    """Test mapping PocketSmith category to ATO category."""
    mapper = ATOCategoryMapper()

    result = mapper.get_ato_category(category_name="Groceries")

    assert result["ato_code"] is None
    assert result["ato_category"] == "Personal expense"
    assert result["deductible"] is False
    assert "Not deductible for individuals" in result["notes"]


def test_get_ato_category_for_business_expense():
    """Test mapping business expense to deductible ATO category."""
    mapper = ATOCategoryMapper()

    result = mapper.get_ato_category(category_name="Office Supplies")

    assert result["ato_code"] == "D5"
    assert result["ato_category"] == "Work-related other expenses"
    assert result["deductible"] is True


def test_get_ato_category_for_unmapped_category():
    """Test handling of unmapped category."""
    mapper = ATOCategoryMapper()

    result = mapper.get_ato_category(category_name="Unknown Category")

    assert result["ato_code"] is None
    assert result["ato_category"] == "Uncategorized"
    assert result["deductible"] is False
