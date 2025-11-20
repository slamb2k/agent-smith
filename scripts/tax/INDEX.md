# Tax Intelligence Scripts - Index

**Location:** `/scripts/tax/`
**Purpose:** Australian tax compliance and intelligence features (3-tier system)

## Modules

### ato_categories.py
- **Size:** 4.3 KB
- **Created:** 2025-11-20 (Phase 4, Task 1)
- **Purpose:** Maps PocketSmith categories to ATO tax return categories
- **Class:** ATOCategoryMapper
- **Level:** 1 (Reference & Reporting)
- **Tags:** tax, ato, categories, mappings
- **Tests:** `tests/unit/test_ato_categories.py` (3 tests)

### deduction_detector.py
- **Size:** 14 KB
- **Created:** 2025-11-20 (Phase 4, Task 4)
- **Purpose:** Pattern-based deduction detection with confidence scoring
- **Class:** DeductionDetector
- **Level:** 2 (Smart Categorization Assistant)
- **Features:**
  - Pattern matching (14 patterns)
  - Confidence scoring (high/medium/low)
  - Time-based commuting detection
  - Substantiation threshold checking ($300 default, $75 taxi/Uber)
  - Instant asset write-off detection
  - Batch processing
- **Tags:** tax, deductions, patterns, level-2, substantiation
- **Tests:** `tests/unit/test_deduction_detector.py` (14 tests)

### cgt_tracker.py
- **Size:** 11 KB
- **Created:** 2025-11-20 (Phase 4, Task 5)
- **Purpose:** Capital Gains Tax tracking with FIFO matching
- **Classes:** CGTTracker, Asset, CGTEvent, AssetType (enum)
- **Level:** 2 (Smart Categorization Assistant)
- **Features:**
  - Track asset purchases (shares, crypto, property)
  - FIFO matching for sales
  - Cost base calculation (price + fees)
  - Holding period calculation
  - 50% CGT discount eligibility (> 365 days)
  - Financial year reporting (AU: July 1 - June 30)
  - Capital gains/loss calculation
- **Tags:** tax, cgt, capital-gains, fifo, level-2, investments
- **Tests:** `tests/unit/test_cgt_tracker.py` (17 tests)

### reporting.py
- **Size:** 5.0 KB
- **Created:** 2025-11-20 (Phase 4, Task 2)
- **Purpose:** Tax-specific report generation
- **Functions:** generate_tax_summary, calculate_gst_from_transactions
- **Level:** 1 (Reference & Reporting)
- **Tags:** tax, reporting, gst, summaries
- **Tests:** `tests/unit/test_tax_reporting.py` (5 tests)

## Tax Intelligence Levels

### Level 1: Reference & Reporting (Implemented)
- ✅ ATO category mappings
- ✅ Basic tax reports
- ✅ GST tracking

### Level 2: Smart Categorization Assistant (Implemented)
- ✅ Deduction detection
- ✅ Confidence scoring
- ✅ Substantiation checking
- ✅ Commuting detection
- ✅ CGT tracking (FIFO, holding periods, discount eligibility)
- ⬜ Expense splitting suggestions (future)
- ⬜ Home office calculations (future)

### Level 3: Full Compliance Suite (Future)
- ⬜ BAS preparation
- ⬜ Compliance checks
- ⬜ Scenario planning
- ⬜ Audit-ready documentation

## Data Files

- `data/tax/ato_category_mappings.json` - Category to ATO code mappings
- `data/tax/deduction_patterns.json` - Deduction detection patterns

## Test Coverage

- **Total tests:** 39 (3 + 14 + 5 + 17)
- **Pass rate:** 100%
- **Files:** 4 test files in `tests/unit/`

## Usage Examples

### ATO Category Mapping
```python
from scripts.tax.ato_categories import ATOCategoryMapper

mapper = ATOCategoryMapper()
ato_info = mapper.get_ato_category("Office Supplies")
# Returns: {ato_code: "D5", ato_category: "Work-related other expenses", ...}
```

### Deduction Detection
```python
from scripts.tax.deduction_detector import DeductionDetector

detector = DeductionDetector()
result = detector.detect_deduction(transaction)
# Returns: {is_deductible: True, confidence: "high", reason: "...", ...}

# Batch processing
results = detector.detect_deductions_batch(transactions)
summary = detector.get_deductible_summary(transactions)
```

### Tax Reporting
```python
from scripts.tax.reporting import generate_tax_summary

summary = generate_tax_summary(transactions)
# Returns: {total_deductible: 5000.00, by_category: {...}, ...}
```

### Capital Gains Tracking
```python
from scripts.tax.cgt_tracker import CGTTracker, AssetType
from decimal import Decimal
from datetime import date

tracker = CGTTracker()

# Track purchase
tracker.track_purchase(
    asset_type=AssetType.SHARES,
    name="BHP Group",
    quantity=Decimal("100"),
    purchase_date=date(2023, 1, 1),
    purchase_price=Decimal("45.50"),
    fees=Decimal("19.95")
)

# Track sale (auto FIFO matching)
event = tracker.track_sale(
    asset_type=AssetType.SHARES,
    name="BHP Group",
    quantity=Decimal("100"),
    sale_date=date(2024, 6, 1),
    sale_price=Decimal("52.00"),
    fees=Decimal("19.95")
)

print(f"Holding period: {event.holding_period_days} days")
print(f"CGT discount eligible: {event.discount_eligible}")
print(f"Capital gain: ${event.capital_gain}")

# Get FY summary
summary = tracker.calculate_total_capital_gains(2024)  # FY 2023-24
```

## Important Notes

- All Level 3 outputs must include disclaimer: "Consult a registered tax agent for advice"
- Patterns are based on general ATO guidelines - not specific tax advice
- Substantiation thresholds: $300 default, $75 taxi/Uber
- Commuting detection uses weekday time windows (6-9:30am, 4:30-7pm)
- Tax records must be kept for 7 years per ATO requirements

## Related Documentation

- Design spec: `docs/design/2025-11-20-agent-smith-design.md` (Section 5 - Tax Intelligence)
- Data index: `data/tax/INDEX.md`
