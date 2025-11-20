# Scenario Analysis Modules

**Last Updated:** 2025-11-21
**Phase:** 5 of 8
**Status:** ✅ COMPLETE

This directory contains all scenario analysis modules for Agent Smith, providing historical "what-if" modeling, future spending projections, optimization suggestions, tax scenario planning, cash flow forecasting, and goal tracking.

---

## Module Overview

| Module | Description | Functions | Tests |
|--------|-------------|-----------|-------|
| `historical.py` | Historical what-if scenario analysis | 1 | 3 unit |
| `projections.py` | Future spending forecasts | 2 | 4 unit |
| `optimization.py` | Savings optimization engine | 2 | 5 unit |
| `tax_scenarios.py` | Tax planning scenarios | 2 | 4 unit |
| `cash_flow.py` | Cash flow forecasting | 2 | 4 unit |
| `goals.py` | Goal tracking and progress | 2 | 3 unit |

**Total:** 6 modules, 11 functions, 23 unit tests + 7 integration tests = 30 tests

---

## Module Details

### historical.py - Historical Scenario Analysis

**Purpose:** Calculate "what-if" scenarios based on historical transaction data.

**Functions:**

#### `calculate_what_if_spending(transactions, category_name, adjustment_percent, start_date=None, end_date=None)`

Calculates the impact of spending adjustments in a specific category.

**Parameters:**
- `transactions` (List[Dict]): Transaction data
- `category_name` (str): Category to analyze
- `adjustment_percent` (float): Percentage adjustment (e.g., -30.0 for 30% reduction)
- `start_date` (str, optional): Start date (YYYY-MM-DD)
- `end_date` (str, optional): End date (YYYY-MM-DD)

**Returns:**
```python
{
    "category": str,
    "actual_spent": float,
    "adjusted_spent": float,
    "savings": float,
    "adjustment_percent": float
}
```

**Example:**
```python
from scripts.scenarios.historical import calculate_what_if_spending

scenario = calculate_what_if_spending(
    transactions=transactions,
    category_name="Dining",
    adjustment_percent=-30.0,
    start_date="2025-01-01",
    end_date="2025-12-31"
)
print(f"Potential savings: ${scenario['savings']:.2f}")
```

---

### projections.py - Future Spending Forecasts

**Purpose:** Project future spending based on historical patterns with inflation adjustments.

**Functions:**

#### `forecast_spending(transactions, category_name, months_forward, inflation_rate=0.0, start_date=None, end_date=None)`

Projects future spending for a category based on historical data.

**Parameters:**
- `transactions` (List[Dict]): Transaction data
- `category_name` (str): Category to forecast
- `months_forward` (int): Number of months to project
- `inflation_rate` (float): Annual inflation rate percentage (default: 0.0)
- `start_date` (str, optional): Historical period start (YYYY-MM-DD)
- `end_date` (str, optional): Historical period end (YYYY-MM-DD)

**Returns:**
```python
{
    "category": str,
    "historical_monthly_average": float,
    "months_forward": int,
    "inflation_rate": float,
    "projected_total": float,
    "projected_monthly": float
}
```

#### `check_affordability(transactions, purchase_amount, target_category, savings_percent=20.0, months_ahead=12)`

Checks if a large purchase is affordable based on projected discretionary income.

**Parameters:**
- `transactions` (List[Dict]): Transaction data
- `purchase_amount` (float): Amount to purchase
- `target_category` (str): Category to reduce spending in
- `savings_percent` (float): Percentage of discretionary income to save (default: 20.0)
- `months_ahead` (int): Months to save (default: 12)

**Returns:**
```python
{
    "purchase_amount": float,
    "monthly_income": float,
    "monthly_expenses": float,
    "discretionary_income": float,
    "monthly_savings": float,
    "total_savings": float,
    "is_affordable": bool,
    "shortfall": float
}
```

**Example:**
```python
from scripts.scenarios.projections import forecast_spending, check_affordability

# Forecast spending
forecast = forecast_spending(
    transactions=transactions,
    category_name="Groceries",
    months_forward=6,
    inflation_rate=3.0
)
print(f"Projected total: ${forecast['projected_total']:.2f}")

# Check affordability
affordability = check_affordability(
    transactions=transactions,
    purchase_amount=5000.0,
    target_category="Entertainment",
    savings_percent=30.0
)
print(f"Affordable: {affordability['is_affordable']}")
```

---

### optimization.py - Savings Optimization Engine

**Purpose:** Identify optimization opportunities in spending patterns.

**Functions:**

#### `suggest_optimizations(transactions, min_savings=50.0, start_date=None, end_date=None)`

Analyzes transactions to suggest optimization opportunities.

**Parameters:**
- `transactions` (List[Dict]): Transaction data
- `min_savings` (float): Minimum annual savings to report (default: 50.0)
- `start_date` (str, optional): Analysis period start (YYYY-MM-DD)
- `end_date` (str, optional): Analysis period end (YYYY-MM-DD)

**Returns:**
```python
{
    "subscriptions": List[Dict],  # Detected subscriptions
    "recurring_expenses": List[Dict],  # High-frequency expenses
    "trending_up": List[Dict],  # Categories with increasing trends
    "potential_annual_savings": float
}
```

#### `detect_subscriptions(transactions, min_occurrences=3, max_day_variance=3, start_date=None, end_date=None)`

Detects recurring subscription payments.

**Parameters:**
- `transactions` (List[Dict]): Transaction data
- `min_occurrences` (int): Minimum occurrences to classify as subscription (default: 3)
- `max_day_variance` (int): Maximum day-of-month variance (default: 3)
- `start_date` (str, optional): Analysis period start (YYYY-MM-DD)
- `end_date` (str, optional): Analysis period end (YYYY-MM-DD)

**Returns:**
```python
List[{
    "merchant": str,
    "amount": float,
    "frequency": int,
    "category": str,
    "annual_cost": float
}]
```

**Example:**
```python
from scripts.scenarios.optimization import suggest_optimizations, detect_subscriptions

# Get optimization suggestions
optimizations = suggest_optimizations(transactions=transactions)
print(f"Potential savings: ${optimizations['potential_annual_savings']:.2f}")

# Detect subscriptions
subscriptions = detect_subscriptions(transactions=transactions)
for sub in subscriptions:
    print(f"{sub['merchant']}: ${sub['annual_cost']:.2f}/year")
```

---

### tax_scenarios.py - Tax Planning Scenarios

**Purpose:** Model tax optimization strategies and deduction planning.

**Functions:**

#### `model_deduction_scenario(transactions, additional_deductions, start_date=None, end_date=None)`

Models the impact of additional tax deductions.

**Parameters:**
- `transactions` (List[Dict]): Transaction data
- `additional_deductions` (List[Dict]): Deductions to add (category, amount)
- `start_date` (str, optional): Tax period start (YYYY-MM-DD)
- `end_date` (str, optional): Tax period end (YYYY-MM-DD)

**Returns:**
```python
{
    "current_deductions": float,
    "additional_deductions": float,
    "total_deductions": float,
    "tax_bracket": float,
    "estimated_tax_savings": float
}
```

#### `compare_tax_structures(transactions, income, scenarios, start_date=None, end_date=None)`

Compares different tax structure scenarios (sole trader vs company).

**Parameters:**
- `transactions` (List[Dict]): Transaction data
- `income` (float): Annual income
- `scenarios` (List[str]): Tax structures to compare (e.g., ["sole_trader", "company"])
- `start_date` (str, optional): Tax period start (YYYY-MM-DD)
- `end_date` (str, optional): Tax period end (YYYY-MM-DD)

**Returns:**
```python
{
    "income": float,
    "deductible_expenses": float,
    "scenarios": List[{
        "structure": str,
        "tax_rate": float,
        "tax_owed": float,
        "net_income": float
    }],
    "recommended": str
}
```

**Example:**
```python
from scripts.scenarios.tax_scenarios import model_deduction_scenario, compare_tax_structures

# Model deduction scenario
scenario = model_deduction_scenario(
    transactions=transactions,
    additional_deductions=[
        {"category": "Home Office", "amount": 5000.0},
        {"category": "Training", "amount": 2000.0}
    ]
)
print(f"Tax savings: ${scenario['estimated_tax_savings']:.2f}")

# Compare tax structures
comparison = compare_tax_structures(
    transactions=transactions,
    income=120000.0,
    scenarios=["sole_trader", "company"]
)
print(f"Recommended: {comparison['recommended']}")
```

---

### cash_flow.py - Cash Flow Forecasting

**Purpose:** Forecast cash flow and monitor emergency fund health.

**Functions:**

#### `forecast_cash_flow(transactions, months_forward=12, start_date=None, end_date=None)`

Forecasts future cash flow based on historical patterns.

**Parameters:**
- `transactions` (List[Dict]): Transaction data
- `months_forward` (int): Number of months to forecast (default: 12)
- `start_date` (str, optional): Historical period start (YYYY-MM-DD)
- `end_date` (str, optional): Historical period end (YYYY-MM-DD)

**Returns:**
```python
{
    "monthly_income": float,
    "monthly_expenses": float,
    "net_cash_flow": float,
    "months_forward": int,
    "projected_cash_flow": float
}
```

#### `track_emergency_fund(transactions, target_months=6, start_date=None, end_date=None)`

Tracks progress toward emergency fund target.

**Parameters:**
- `transactions` (List[Dict]): Transaction data
- `target_months` (int): Target months of expenses (default: 6)
- `start_date` (str, optional): Analysis period start (YYYY-MM-DD)
- `end_date` (str, optional): Analysis period end (YYYY-MM-DD)

**Returns:**
```python
{
    "monthly_expenses": float,
    "target_months": int,
    "target_amount": float,
    "current_balance": float,
    "coverage_months": float,
    "shortfall": float
}
```

**Example:**
```python
from scripts.scenarios.cash_flow import forecast_cash_flow, track_emergency_fund

# Forecast cash flow
forecast = forecast_cash_flow(
    transactions=transactions,
    months_forward=12
)
print(f"Projected cash flow: ${forecast['projected_cash_flow']:.2f}")

# Track emergency fund
emergency = track_emergency_fund(
    transactions=transactions,
    target_months=6
)
print(f"Coverage: {emergency['coverage_months']:.1f} months")
```

---

### goals.py - Goal Tracking

**Purpose:** Track progress toward financial goals.

**Functions:**

#### `track_goal_progress(transactions, goal_amount, category_name, start_date=None, end_date=None)`

Tracks progress toward a savings or spending goal.

**Parameters:**
- `transactions` (List[Dict]): Transaction data
- `goal_amount` (float): Target goal amount
- `category_name` (str): Category to track
- `start_date` (str, optional): Tracking period start (YYYY-MM-DD)
- `end_date` (str, optional): Tracking period end (YYYY-MM-DD)

**Returns:**
```python
{
    "goal_amount": float,
    "current_amount": float,
    "progress_percent": float,
    "remaining": float,
    "is_complete": bool
}
```

#### `project_goal_completion(transactions, goal_amount, category_name, start_date=None, end_date=None)`

Projects when a goal will be achieved based on current trends.

**Parameters:**
- `transactions` (List[Dict]): Transaction data
- `goal_amount` (float): Target goal amount
- `category_name` (str): Category to track
- `start_date` (str, optional): Historical period start (YYYY-MM-DD)
- `end_date` (str, optional): Historical period end (YYYY-MM-DD)

**Returns:**
```python
{
    "goal_amount": float,
    "current_amount": float,
    "monthly_average": float,
    "months_to_completion": int,
    "can_complete": bool
}
```

**Example:**
```python
from scripts.scenarios.goals import track_goal_progress, project_goal_completion

# Track goal progress
progress = track_goal_progress(
    transactions=transactions,
    goal_amount=10000.0,
    category_name="Vacation Fund"
)
print(f"Progress: {progress['progress_percent']:.1f}%")

# Project completion
projection = project_goal_completion(
    transactions=transactions,
    goal_amount=10000.0,
    category_name="Vacation Fund"
)
print(f"Months to goal: {projection['months_to_completion']}")
```

---

## Integration Tests

All scenario modules are tested together in the integration test suite:

**Location:** `tests/integration/test_scenario_analysis.py`

**Test Coverage:**
- End-to-end scenario workflows
- Cross-module integration
- Real PocketSmith data validation
- Complete scenario pipeline testing

**Integration Tests:** 7 tests covering:
1. What-if analysis workflow
2. Spending projections with inflation
3. Affordability checking
4. Subscription detection workflow
5. Tax scenario modeling
6. Cash flow forecasting
7. Optimization suggestions

---

## Usage Notes

### Transaction Data Format

All functions expect transactions in PocketSmith API format:

```python
{
    "id": int,
    "date": str,  # YYYY-MM-DD
    "amount": float,  # Negative for expenses, positive for income
    "category": {
        "id": int,
        "title": str
    },
    "payee": str,
    "memo": str
}
```

### Date Filtering

All functions support optional date filtering:
- If `start_date` and `end_date` are omitted, all transactions are analyzed
- Dates must be in ISO 8601 format (YYYY-MM-DD)
- Date comparisons use string sorting (efficient for ISO dates)

### Error Handling

- All functions validate input parameters
- Invalid dates or missing data return appropriate error messages
- Empty transaction lists return valid results with zero values

---

## Future Enhancements

Planned for Phase 6 (Orchestration & UX):
- Slash command integration (`/agent-smith-scenario`)
- Subagent orchestration for heavy computations
- Batch scenario processing
- Scenario comparison UI
- Report generation integration
- Multi-scenario optimization

---

**Last Updated:** 2025-11-21
**Module Count:** 6
**Function Count:** 11
**Test Count:** 30 (23 unit + 7 integration)
