"""Test script for category visualizer."""

from typing import Any, Dict, List
from scripts.utils.category_visualizer import CategoryVisualizer

# Example existing categories (simplified PocketSmith structure)
existing_categories: List[Dict[str, Any]] = [
    {"name": "Income", "parent": None},
    {"name": "Salary", "parent": "Income"},
    {"name": "Expenses", "parent": None},
    {"name": "Food", "parent": "Expenses"},
    {"name": "Transport", "parent": "Expenses"},
]

# Example new categories (after applying template)
new_categories: List[Dict[str, Any]] = [
    {"name": "Income", "parent": None},
    {"name": "Salary/Wages", "parent": "Income"},  # Renamed from "Salary"
    {"name": "Interest Income", "parent": "Income"},  # NEW
    {"name": "Food & Dining", "parent": None},  # NEW (moved from under Expenses)
    {"name": "Groceries", "parent": "Food & Dining"},  # NEW
    {"name": "Restaurants", "parent": "Food & Dining"},  # NEW
    {"name": "Transportation", "parent": None},  # NEW (moved from under Expenses)
    {"name": "Fuel", "parent": "Transportation"},  # NEW
    {"name": "Public Transport", "parent": "Transportation"},  # NEW
]

visualizer = CategoryVisualizer(use_colors=True)

# Test 1: Simple tree rendering
print("=" * 70)
print("TEST 1: Simple Tree Rendering")
print("=" * 70)
print(visualizer.render_tree(new_categories, title="New Category Structure"))

# Test 2: Change detection
print("\n\n" + "=" * 70)
print("TEST 2: Change Detection")
print("=" * 70)
changes = visualizer.detect_changes(existing_categories, new_categories, strategy="smart_merge")
for name, change in changes.items():
    print(f"{name}: {change.change_type}")

# Test 3: Side-by-side comparison
print("\n\n" + "=" * 70)
print("TEST 3: Side-by-Side Comparison")
print("=" * 70)
print(visualizer.render_side_by_side(existing_categories, new_categories, changes))

# Test 4: Compact list view
print("\n\n" + "=" * 70)
print("TEST 4: Compact List View")
print("=" * 70)
print(visualizer.render_compact_list(new_categories, changes))
