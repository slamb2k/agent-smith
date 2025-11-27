---
title: PocketSmith API Budgeting Guide
category: ai_docs
status: active
created: 2025-11-27
last_updated: 2025-11-27
tags: [pocketsmith, api, budgeting, forecasting, analysis]
source: https://developers.pocketsmith.com/docs/budgeting
---

# PocketSmith API Budgeting Guide

A budget in PocketSmith is formed by the placement of budget events on the forecast calendar. For example, setting up an event for the Food category that repeats every week will form a weekly budget. However, placement of events can be arbitrary -- they could be a mixture of one off, yearly, and quarterly events for a single category.

The budget reporting API serves one core purpose: **to report, in a variety of different ways, the actual spending and earning versus forecasted (budgeted) earning and spending.**

## Data Modelling

### Budget Analysis Package

At the core of the data you'll be working with is the **budget analysis**. A budget analysis will either be analysing income, or analysing expense. These are wrapped in a **budget analysis package**, which provides an income analysis or an expense analysis, or both where applicable.

### Noncontextual Package Example

```json
{
  "income": null,
  "expense": {
    "start_date": "2016-11-01",
    "end_date": "2016-11-30",
    "total_actual_amount": -20.0,
    "average_actual_amount": -20.0,
    "total_forecast_amount": 0,
    "average_forecast_amount": 0.0,
    "total_under_by": 0,
    "total_over_by": 0,
    "periods": [
      {
        "start_date": "2016-11-01",
        "end_date": "2016-11-30",
        "actual_amount": -20.0,
        "forecast_amount": 0,
        "refund_amount": 0,
        "current": true,
        "over_budget": false,
        "under_budget": true,
        "over_by": 0,
        "under_by": 0,
        "percentage_used": 0
      }
    ]
  }
}
```

### Contextual vs Noncontextual Packages

| Type | Description | Extra Fields |
|------|-------------|--------------|
| **Noncontextual** | Just income and expense analysis provided | None |
| **Contextual** | Analysis for a specific category | `category` - the single category being analysed |
|                |                                   | `is_transfer` - whether analyses look like transfers |

### Understanding the Data

- **Amounts are signed**: Expense analysis has negative amounts, income analysis has positive amounts
- **Periods array**: Contains one or more period analyses splitting up the date range
- **actual_amount**: What was actually spent/earned
- **forecast_amount**: What was budgeted

## Period Types

The period defines how the budget analysis should be split up across the date range.

### Time Period Analysis

Splits the date range over a time period (e.g., `2 weeks` for fortnightly). The forecast events that fall in that date range, as well as the actuals (transactions), will be included.

### Event Period Analysis

A special case where the budget events themselves form the period. This is what the user intends when they set up a repeating budget in PocketSmith.

**Example:** If a weekly repeating budget starts on 2016-09-01, and is requested to be analysed from 2016-09-01 to 2016-09-30:

| Period | Start Date | End Date |
|--------|------------|----------|
| 1 | 2016-09-01 | 2016-09-07 |
| 2 | 2016-09-08 | 2016-09-14 |
| 3 | 2016-09-15 | 2016-09-21 |
| 4 | 2016-09-22 | 2016-09-28 |
| 5 | 2016-09-29 | 2016-10-05 |

**Note:** The end date may be pushed out to accommodate full periods.

### When Event Period Analysis Fails

Event period analysis may not be possible when:
- User has multiple sets of budget events for a category with overlapping dates
- Multiple categories are included with different repeating sequences

In these cases, the API suggests a time period alternative (e.g., `1 months`).

## API Endpoints

### 1. List User's Budget

**Endpoint:** `GET /v2/users/{id}/budget`

Returns the user's budgeted categories analysed currently in the event period. Shows progress toward each forecasted amount.

**Features:**
- Returns array of **contextual** budget analysis packages
- Only one period analysis (the current period)
- Use `roll_up=1` to combine subcategory budgets into parent

**Response:** Array of contextual budget analysis packages

### 2. Get Budget Summary

**Endpoint:** `GET /v2/users/{id}/budget_summary`

A shortcut for analysing all user's categories for a certain time period. Represents expense vs income actuals vs forecasted.

**Response:** Noncontextual analysis package

### 3. Get Trend Analysis

**Endpoint:** `GET /v2/budget_analysis_packages/{id}`

A raw query to the budgeting system. Request analysis with:
- Specific categories
- Specific scenarios
- Date range
- Period type

**Response:** Noncontextual analysis package

### Handling Time Period Alternatives

If you attempt event period analysis and it's not possible, you'll receive:
- **Status:** 422 Unprocessable Entity
- **Headers:**
  - `X-Suggested-Time-Period-Alternative-Type` (e.g., weeks, months)
  - `X-Suggested-Time-Period-Alternative-Interval` (integer)

Make the request again using the suggested period type and interval.

## Example: Fetching Budget Overview

```python
def get_budget_overview(user_id, api_key):
    """Get the user's current budget overview."""
    url = f"https://api.pocketsmith.com/v2/users/{user_id}/budget"
    headers = {"X-Developer-Key": api_key}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    budgets = response.json()

    for budget in budgets:
        category = budget.get("category", {})
        expense = budget.get("expense", {})

        if expense:
            period = expense["periods"][0] if expense["periods"] else {}
            print(f"{category.get('title')}: "
                  f"${abs(period.get('actual_amount', 0)):.2f} / "
                  f"${abs(period.get('forecast_amount', 0)):.2f} "
                  f"({period.get('percentage_used', 0)}%)")

    return budgets
```

## Best Practices

1. **Use Roll-Up for Hierarchical Budgets** - When displaying budget summaries, use `roll_up=1` to combine subcategory spending into parent categories.

2. **Handle 422 Responses Gracefully** - When event period analysis fails, automatically retry with the suggested time period alternative.

3. **Include All Scenarios** - For comprehensive trend analysis, collect scenarios from all user accounts and include them in your request.

4. **Watch for Signed Amounts** - Remember that expense amounts are negative and income amounts are positive.
