# Orchestration Layer

Smart subagent conductor for intelligent delegation and context preservation.

## Modules

### conductor.py

Core orchestration logic for subagent management.

**Key Classes:**
- `OperationType` - Enum for operation classification
- `SubagentConductor` - Main orchestration coordinator
- `ContextManager` - User context preservation
- `ResultAggregator` - Parallel result aggregation

**Key Functions:**
- `should_delegate()` - Decision logic for delegation

## API Reference

### should_delegate()

```python
def should_delegate(
    operation_type: OperationType,
    transaction_count: int,
    estimated_tokens: int,
    can_parallelize: bool,
) -> bool
```

Determine if operation should be delegated to subagent.

**Parameters:**
- `operation_type` - Type of operation
- `transaction_count` - Number of transactions involved
- `estimated_tokens` - Estimated token count
- `can_parallelize` - Whether operation can be parallelized

**Returns:** `True` if should delegate

**Delegation Rules:**
- Always delegate: BULK_PROCESSING, DEEP_ANALYSIS, MULTI_PERIOD
- Transaction count > 100
- Estimated tokens > 5000
- Can parallelize

### SubagentConductor

```python
class SubagentConductor:
    def __init__(
        self,
        transaction_threshold: int = 100,
        token_threshold: int = 5000,
        dry_run: bool = False,
    )
```

Intelligent orchestration for subagent delegation.

**Methods:**

#### estimate_complexity()

```python
def estimate_complexity(
    self,
    operation_type: OperationType,
    transaction_count: int,
    period_months: int = 1,
    categories: int = 1,
) -> Dict[str, Any]
```

Estimate computational complexity.

**Returns:**
```python
{
    "estimated_tokens": 2250,
    "can_parallelize": True,
    "suggested_subagents": 3
}
```

#### build_subagent_prompt()

```python
def build_subagent_prompt(
    self,
    operation_type: str,
    task_description: str,
    data_summary: str,
    intelligence_mode: str = "smart",
    tax_level: str = "smart",
    constraints: Optional[Dict[str, Any]] = None,
) -> str
```

Build delegation prompt for subagent.

**Returns:** Formatted prompt with context, data, references, and constraints.

### ContextManager

```python
class ContextManager:
    def __init__(self, user_id: str)
```

Manages user context across subagent operations.

**Methods:**
- `set_preference(key, value)` - Store user preference
- `get_preference(key, default=None)` - Retrieve preference
- `update_session_state(key, value)` - Update session state
- `get_session_state(key, default=None)` - Retrieve state

### ResultAggregator

```python
class ResultAggregator:
    def __init__(self)
```

Aggregates results from multiple subagent operations.

**Methods:**

#### add_result()

```python
def add_result(
    self,
    operation: str,
    status: str,
    data: Dict[str, Any]
) -> None
```

Add result from a subagent operation.

#### merge_results()

```python
def merge_results(self, operation_type: str) -> Dict[str, Any]
```

Merge multiple subagent results into summary.

**Returns:**
```python
{
    "status": "success",
    "operation_type": "categorization",
    "total_operations": 3,
    "successful_operations": 3,
    "failed_operations": 0,
    "aggregated_data": {
        "categorized": 135,
        "skipped": 15
    }
}
```

## Usage Examples

### Basic Delegation Decision

```python
from scripts.orchestration.conductor import SubagentConductor, OperationType

conductor = SubagentConductor()

# Check if should delegate
should_delegate = conductor.should_delegate_operation(
    operation_type=OperationType.CATEGORIZATION,
    transaction_count=150
)

if should_delegate:
    print("Delegating to subagent...")
else:
    print("Handling directly...")
```

### Context Preservation

```python
from scripts.orchestration.conductor import ContextManager

context = ContextManager(user_id="12345")

# Set preferences
context.set_preference("intelligence_mode", "aggressive")
context.set_preference("tax_level", "full")

# Track session state
context.update_session_state("last_operation", "categorization")
context.update_session_state("transactions_processed", 150)

# Retrieve later
mode = context.get_preference("intelligence_mode")
```

### Parallel Result Aggregation

```python
from scripts.orchestration.conductor import ResultAggregator

aggregator = ResultAggregator()

# Add results from parallel subagents
aggregator.add_result("batch1", "success", {"categorized": 50})
aggregator.add_result("batch2", "success", {"categorized": 45})
aggregator.add_result("batch3", "success", {"categorized": 40})

# Merge into summary
merged = aggregator.merge_results(operation_type="categorization")
print(f"Total categorized: {merged['aggregated_data']['categorized']}")
```

## Tests

- **Unit tests:** `tests/unit/test_conductor.py`, `tests/unit/test_context_preservation.py`
- **Integration tests:** `tests/integration/test_orchestration.py`
- **Test count:** 25 unit tests, 6 integration tests

## Future Enhancements

- Subagent health monitoring
- Rate limiting across subagents
- Retry logic for failed operations
- Cost tracking and optimization
- Performance analytics
