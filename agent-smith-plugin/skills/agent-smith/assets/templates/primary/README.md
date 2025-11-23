# Primary Income Templates

Choose ONE template that matches your main source of income.

## Available Templates

- `payg-employee.yaml` - Salary/wage earner
- `sole-trader.yaml` - ABN holder, contractor, quarterly BAS
- `small-business.yaml` - Business owner with employees
- `retiree.yaml` - Superannuation/pension income
- `student.yaml` - Minimal income, government payments, HECS

## YAML Schema

```yaml
name: Template Name
layer: primary
description: |
  Multi-line description of this template.

categories:
  - name: "Category Name"
    parent: null  # or "Parent Category Name"
    description: "Category purpose"

rules:
  - id: unique-rule-id
    pattern: "regex pattern"
    category: "Target Category"
    confidence: high|medium|low
    description: "What this rule does"

tax_tracking:
  bas_enabled: true|false
  gst_method: cash|accrual
  # ... other tax config

alerts:
  - type: alert_type
    schedule: quarterly|monthly
    message: "Alert message"

dependencies:
  requires: []
  conflicts_with: ["other-template-id"]

metadata:
  created: "YYYY-MM-DD"
  version: "1.0.0"
  priority: 1
```
