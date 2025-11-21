# Interactive Workflows

Guided workflows for multi-step operations with user interaction.

## Modules

### categorization.py

Interactive transaction categorization workflow.

## API Reference

### parse_categorize_args()

```python
def parse_categorize_args(args: List[str]) -> Dict[str, Any]
```

Parse arguments for categorization command.

**Returns:**
```python
{
    "mode": "smart",
    "period": "2025-11",
    "account": None,
    "dry_run": False
}
```

### CategorizationWorkflow

```python
class CategorizationWorkflow:
    def __init__(self, client, mode: str = "smart")
```

Interactive workflow for transaction categorization.

**Methods:**

#### should_use_subagent()

```python
def should_use_subagent(self, transaction_count: int) -> bool
```

Determine if should use subagent for categorization.

#### build_summary()

```python
def build_summary(self, results: Dict[str, Any], total: int) -> str
```

Build human-readable summary of categorization results.

## Usage Examples

### Categorization Workflow

```python
from scripts.workflows.categorization import CategorizationWorkflow, parse_categorize_args
from scripts.api.client import PocketSmithClient

# Parse command arguments
args = parse_categorize_args(["--mode=smart", "--period=2025-11"])

# Create workflow
client = PocketSmithClient(api_key="your-key")
workflow = CategorizationWorkflow(client, mode=args["mode"])

# Check delegation
if workflow.should_use_subagent(transaction_count=150):
    print("Using subagent for large batch...")
else:
    print("Handling directly...")

# Build summary
results = {"categorized": 85, "skipped": 15, "rules_applied": 12, "new_rules": 3}
summary = workflow.build_summary(results, total=100)
print(summary)
```

## Tests

- **Unit tests:** `tests/unit/test_categorization_workflow.py`
- **Test count:** 7 unit tests

## Future Workflows

- Analysis workflow (spending, trends, insights)
- Reporting workflow (multi-format generation)
- Optimization workflow (categories, rules, spending)
- Tax workflow (deductions, CGT, BAS)
- Health check workflow (6 health scores)
