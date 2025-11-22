# Rule Learning Example

This document demonstrates the rule learning functionality in the enhanced CategorizationWorkflow.

## Scenario

A user has transactions from various merchants. Initially, there are no rules, so the LLM categorizes them. The workflow suggests creating rules for consistent patterns.

## Step-by-Step Example

### Step 1: Initial Transaction (No Rules)

```python
from scripts.workflows.categorization import CategorizationWorkflow
from scripts.core.unified_rules import UnifiedRuleEngine

# Start with empty rules
engine = UnifiedRuleEngine()  # No rules.yaml yet
workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)

transaction = {
    "id": 101,
    "payee": "WOOLWORTHS METRO 123 SYDNEY",
    "amount": -67.85,
    "date": "2025-11-20",
}

categories = [
    {"title": "Groceries", "parent": ""},
    {"title": "Shopping", "parent": ""},
    {"title": "Transport", "parent": ""},
]

# Categorize (will fall back to LLM)
result = workflow.categorize_transaction(transaction, available_categories=categories)
```

**Result:**
```python
{
    "category": "Groceries",
    "labels": [],
    "confidence": 90,
    "source": "llm",
    "llm_used": True,
    "reasoning": "Woolworths is a major Australian supermarket chain"
}
```

### Step 2: Learn Rule from LLM Result

```python
# Suggest a rule based on this LLM categorization
rule_suggestion = workflow.suggest_rule_from_llm_result(transaction, result)

print(rule_suggestion)
```

**Output:**
```python
{
    "type": "category",
    "name": "WOOLWORTHS → Groceries",
    "patterns": ["WOOLWORTHS"],
    "category": "Groceries",
    "confidence": 90
}
```

### Step 3: User Approves and Adds Rule

User reviews the suggestion and adds it to `data/rules.yaml`:

```yaml
rules:
  - type: category
    name: WOOLWORTHS → Groceries
    patterns: [WOOLWORTHS]
    category: Groceries
    confidence: 95  # User can adjust confidence
```

### Step 4: Subsequent Transactions Use Rule

```python
# Reload engine with new rules
engine = UnifiedRuleEngine()  # Loads rules.yaml
workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)

# New Woolworths transaction
transaction2 = {
    "id": 102,
    "payee": "WOOLWORTHS ONLINE ORDER 456",
    "amount": -123.45,
    "date": "2025-11-21",
}

# Categorize (will use rule, no LLM needed)
result2 = workflow.categorize_transaction(transaction2, available_categories=categories)
```

**Result:**
```python
{
    "category": "Groceries",
    "labels": [],
    "confidence": 95,
    "source": "rule",
    "llm_used": False,  # ← No LLM call needed!
}
```

## Advanced: Batch Learning

Process multiple new merchants and learn rules from all of them:

```python
transactions = [
    {"id": 1, "payee": "COLES EXPRESS 789", "amount": -45.20},
    {"id": 2, "payee": "BP PETROL STATION", "amount": -80.00},
    {"id": 3, "payee": "UBER TRIP #ABC123", "amount": -25.50},
    {"id": 4, "payee": "NETFLIX.COM", "amount": -16.99},
]

learned_rules = []

for txn in transactions:
    result = workflow.categorize_transaction(txn, available_categories=categories)

    if result["source"] == "llm" and result["confidence"] >= 85:
        # High confidence LLM result - suggest rule
        rule = workflow.suggest_rule_from_llm_result(txn, result)
        learned_rules.append(rule)
        print(f"Learned: {rule['name']}")

# learned_rules:
# [
#     {"name": "COLES → Groceries", "patterns": ["COLES"], ...},
#     {"name": "BP → Transport", "patterns": ["BP"], ...},
#     {"name": "UBER → Transport", "patterns": ["UBER"], ...},
#     {"name": "NETFLIX.COM → Entertainment", "patterns": ["NETFLIX.COM"], ...},
# ]
```

## Intelligence Mode Impact on Learning

Different modes affect which LLM results are considered for rule learning:

### Conservative Mode
```python
workflow = CategorizationWorkflow(client=None, mode="conservative", rule_engine=engine)

# Conservative: Only suggest rules for 95%+ confidence
# (Since conservative never auto-applies, user reviews everything anyway)
```

### Smart Mode (Default)
```python
workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)

# Smart: Suggest rules for 90%+ confidence
# These would auto-apply if they were rules
```

### Aggressive Mode
```python
workflow = CategorizationWorkflow(client=None, mode="aggressive", rule_engine=engine)

# Aggressive: Suggest rules for 80%+ confidence
# More liberal, learns more rules but may be less accurate
```

## Rule Suggestion Criteria

A rule is suggested when:
1. ✅ Source is "llm" (not "rule" or "none")
2. ✅ Category is not None
3. ✅ Merchant name can be extracted from payee
4. ✅ (Optional) Confidence meets minimum threshold

**Not suggested when:**
- ❌ Already matched by rule
- ❌ LLM returned no result
- ❌ Payee cannot be parsed (no clear merchant name)

## Merchant Name Extraction

The `_extract_merchant_name()` method handles various payee formats:

```python
# Examples of merchant extraction:

"WOOLWORTHS METRO 123"           → "WOOLWORTHS"
"COLES EXPRESS 789 SYDNEY"       → "COLES"
"BP PETROL STATION #456"         → "BP"
"UBER TRIP #ABC123"              → "UBER"
"NETFLIX.COM AU"                 → "NETFLIX.COM"
"7-ELEVEN STORE 12345"           → "7-ELEVEN"
"COMMONWEALTH BANK ATM"          → "COMMONWEALTH"
```

**Algorithm:**
1. Convert to uppercase
2. Remove trailing numbers: `\s+\d+.*$`
3. Remove hash patterns: `\s+#.*$`
4. Take first word

## Complete Workflow Example

```python
from scripts.workflows.categorization import CategorizationWorkflow
from scripts.core.unified_rules import UnifiedRuleEngine
from pathlib import Path
import yaml

# Initialize
rules_file = Path("data/rules.yaml")
engine = UnifiedRuleEngine(rules_file=rules_file)
workflow = CategorizationWorkflow(client=None, mode="smart", rule_engine=engine)

# Categorize transaction
transaction = {
    "id": 123,
    "payee": "TARGET STORE 456",
    "amount": -89.99,
    "date": "2025-11-22",
}

categories = [{"title": "Shopping", "parent": ""}]
result = workflow.categorize_transaction(transaction, available_categories=categories)

# If LLM was used and confidence is high, learn rule
if result["source"] == "llm" and result["confidence"] >= 90:
    rule_suggestion = workflow.suggest_rule_from_llm_result(transaction, result)

    print(f"\n🎓 Rule Learning Suggestion:")
    print(f"   Merchant: {rule_suggestion['patterns'][0]}")
    print(f"   Category: {rule_suggestion['category']}")
    print(f"   Confidence: {rule_suggestion['confidence']}%")

    # Ask user to approve
    user_approves = True  # In real usage, prompt user

    if user_approves:
        # Add to rules file
        if rules_file.exists():
            with open(rules_file) as f:
                rules_data = yaml.safe_load(f) or {"rules": []}
        else:
            rules_data = {"rules": []}

        rules_data["rules"].append(rule_suggestion)

        with open(rules_file, "w") as f:
            yaml.safe_dump(rules_data, f, sort_keys=False)

        print(f"✅ Rule added to {rules_file}")
        print("   Future transactions from TARGET will use this rule")
```

## Benefits of Rule Learning

1. **Efficiency**: Rules are O(n), LLM is expensive
2. **Consistency**: Same merchant always categorized the same way
3. **Offline**: Rules work without LLM/internet
4. **Speed**: Instant rule matching vs API calls
5. **User Control**: User reviews and approves all learned rules

## Future Enhancements

1. **Auto-learning**: Automatically add rules after N consistent LLM categorizations
2. **Conflict Detection**: Warn if new rule conflicts with existing rules
3. **Confidence Adjustment**: Learn optimal confidence from user corrections
4. **Pattern Refinement**: Suggest better patterns based on transaction history
5. **Bulk Import**: Learn rules from CSV of past categorizations
