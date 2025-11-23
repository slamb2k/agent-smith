---
name: smith:categorize
description: Categorize transactions using the hybrid rule + LLM workflow
argument-hints:
  - "[--mode=conservative|smart|aggressive] [--period=YYYY-MM] [--account=ID] [--dry-run]"
---

Categorize transactions using the hybrid rule + LLM workflow.

You are the Agent Smith categorization assistant with real LLM integration. Your job is to:

1. Ask the user for:
   - Period to process (YYYY-MM or "last-30-days")
   - Intelligence mode (conservative/smart/aggressive)
   - Whether to apply changes or dry-run

2. Execute the categorization workflow with LLM orchestration:

   **Step 2a:** Fetch and categorize transactions using Python:
   ```bash
   uv run python -c "
import sys
import os
import json
from datetime import datetime, timedelta

# Add plugin root to Python path for imports
plugin_root = os.environ.get('CLAUDE_PLUGIN_ROOT', '.')
if plugin_root not in sys.path:
    sys.path.insert(0, plugin_root)

from scripts.core.api_client import PocketSmithClient
from scripts.workflows.categorization import CategorizationWorkflow

# Parameters (will be substituted)
period = '${period}'
mode = '${mode}'
dry_run = ${dry_run}

# Parse period
if period == 'last-30-days':
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
else:
    year, month = period.split('-')
    start_date = datetime(int(year), int(month), 1)
    if int(month) == 12:
        end_date = datetime(int(year) + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(int(year), int(month) + 1, 1) - timedelta(days=1)

# Fetch transactions
client = PocketSmithClient()
user = client.get_user()
transactions = client.get_transactions(
    user_id=user['id'],
    start_date=start_date.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d'),
)

# Filter uncategorized
needs_categorization = [
    t for t in transactions
    if not t.get('category') or t.get('needs_review')
]

if not needs_categorization:
    print(json.dumps({'status': 'no_transactions'}))
    sys.exit(0)

# Get categories
categories = client.get_categories(user['id'])

# Run categorization workflow (in production mode)
workflow = CategorizationWorkflow(client=client, mode=mode)
workflow.llm_orchestrator.test_mode = False  # Enable production mode

result = workflow.categorize_transactions_batch(needs_categorization, categories)

# Output results as JSON
output = {
    'status': 'success',
    'stats': result['stats'],
    'results': result['results'],
    'transactions': needs_categorization,
    'categories': categories,
    'dry_run': dry_run
}
print(json.dumps(output))
"
   ```

   **Step 2b:** Parse the JSON output and handle LLM needs:
   - If workflow returns marker dicts (indicated by logging warnings), those indicate LLM prompts that need execution
   - For each prompt that needs execution:
     - Extract the prompt text
     - Execute it directly using your LLM capabilities
     - Parse the response using the service's parsing methods

   **Step 2c:** Apply results to PocketSmith (if not dry-run):
   - For each categorized transaction, update via API
   - Track success/failure counts

3. After processing, show the user:
   - How many transactions were processed
   - Rule matches vs LLM fallbacks
   - Validation results (if any)
   - Any new rules suggested
   - Ask if they want to create rules from high-confidence LLM patterns

4. If user wants to create rules, collect:
   - Which LLM patterns to convert to rules
   - Confirmation before adding to rules.yaml

5. Remind user to restart Claude Code after any rule changes.

**Example interaction:**

```
User: /smith:categorizeAssistant: I'll help categorize your transactions. What period would you like to process?
  - "2025-11" for November 2025
  - "last-30-days" for recent transactions

User: last-30-daysAssistant: What intelligence mode would you like to use?
  - conservative: Manual review for all (safer)
  - smart: Auto-apply 90%+ confidence (recommended)
  - aggressive: Auto-apply 80%+ confidence (faster)

User: smart
Assistant: Would you like to apply changes or run in dry-run mode first?
  - dry-run: Preview only
  - apply: Make actual changes

User: dry-run
Assistant: Running categorization with smart mode in dry-run...

[Executes workflow, shows progress]

✓ Categorized 45/50 transactions
  - Rule matches: 30
  - LLM fallbacks: 12
  - Validations: 8 (6 upgraded)
  - Skipped: 5 (low confidence)

Found 3 high-confidence LLM patterns that could become rules:
1. "NETFLIX" → Entertainment (confidence: 95%)
2. "UBER EATS" → Dining Out (confidence: 92%)
3. "CHEMIST WAREHOUSE" → Health & Medical (confidence: 91%)

Would you like to create rules for any of these patterns?
```
