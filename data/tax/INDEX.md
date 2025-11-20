# Tax Data Directory Index

**Location:** `/data/tax/`
**Purpose:** Tax-related reference data and patterns for Australian tax compliance

## Files

### ato_category_mappings.json
- **Size:** 2.3 KB
- **Created:** 2025-11-20
- **Purpose:** Maps PocketSmith categories to ATO tax return categories
- **Format:** JSON with mappings and ato_categories arrays
- **Used by:** `scripts/tax/ato_categories.py` (ATOCategoryMapper)
- **Tags:** tax, ato, categories, mappings, level-1

### deduction_patterns.json
- **Size:** 8.5 KB
- **Created:** 2025-11-20
- **Purpose:** Pattern-based deduction detection rules for Level 2 tax intelligence
- **Format:** JSON with patterns, substantiation thresholds, commuting hours, confidence scoring
- **Contains:** 14 deduction patterns covering office supplies, computer equipment, professional development, transport, groceries, etc.
- **Used by:** `scripts/tax/deduction_detector.py` (DeductionDetector)
- **Tags:** tax, deductions, patterns, level-2, ato-compliance

## Retention Policy

- **Tax category mappings:** Keep updated annually or when ATO guidelines change
- **Deduction patterns:** Review and update annually before EOFY (May-June)
- **All tax data:** Maintain for 7 years per ATO record-keeping requirements

## Related Files

- `scripts/tax/ato_categories.py` - Category mapper implementation
- `scripts/tax/deduction_detector.py` - Deduction detection implementation
- `ai_docs/tax/` - ATO documentation cache (future)

## Notes

- Always verify patterns against current ATO guidelines
- Patterns are for automated detection only - not tax advice
- Update substantiation thresholds when ATO changes rules
