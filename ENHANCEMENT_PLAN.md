# Enhancement Plan: Smart Account-Based Name Detection

## Problem Statement

Currently, the discovery script:
1. Only looks at **all accounts/categories globally** for name detection
2. Cannot distinguish between household-shared vs parenting-shared accounts
3. Suggests the same names for both contexts (e.g., "Simon and Caitlin" for both)

**User's scenario:**
- Household shared account: "Shared Bills - Simon & Caitlin"
- Parenting shared account: "Kids Account" with Simon and Tori as parents
- System incorrectly suggests "Simon and Caitlin" for both contexts

## Solution Design

### Phase 1: Account Classification

Add method to classify accounts by type:

```python
@dataclass
class AccountClassification:
    """Classification of an account type."""

    account_id: int
    account_name: str
    account_type: str  # "household_shared", "parenting_shared", "individual"
    confidence: float  # 0.0-1.0
    indicators: List[str]  # What keywords/patterns triggered this classification

def _classify_accounts(
    self,
    accounts: List[AccountSummary],
    transactions: List[Dict[str, Any]]
) -> List[AccountClassification]:
    """Classify each account as household-shared, parenting-shared, or individual."""

    classifications = []

    for account in accounts:
        account_name_lower = account.name.lower()

        # Get transactions for this account
        account_txns = [t for t in transactions if t.get("transaction_account", {}).get("id") == account.id]

        # Extract categories used in this account
        account_categories = {t.get("category", {}).get("title", "").lower() for t in account_txns if t.get("category")}

        # Classification logic
        household_indicators = {"shared", "joint", "household", "bills", "house"}
        parenting_indicators = {"kids", "children", "child", "custody", "child support"}

        household_score = sum(1 for ind in household_indicators if ind in account_name_lower)
        household_score += sum(1 for ind in household_indicators if any(ind in cat for cat in account_categories)) * 0.5

        parenting_score = sum(1 for ind in parenting_indicators if ind in account_name_lower)
        parenting_score += sum(1 for ind in parenting_indicators if any(ind in cat for cat in account_categories)) * 0.5

        if household_score > parenting_score and household_score > 0:
            account_type = "household_shared"
            confidence = min(household_score / 3.0, 1.0)
        elif parenting_score > 0:
            account_type = "parenting_shared"
            confidence = min(parenting_score / 3.0, 1.0)
        else:
            account_type = "individual"
            confidence = 0.8

        classifications.append(AccountClassification(
            account_id=account.id,
            account_name=account.name,
            account_type=account_type,
            confidence=confidence,
            indicators=[...]
        ))

    return classifications
```

### Phase 2: Name Extraction from Account Context

Add method to extract person names from account-specific data:

```python
import re

@dataclass
class NameSuggestion:
    """Suggested names for a shared context."""

    context: str  # "household_shared" or "parenting_shared"
    person_1: Optional[str]
    person_2: Optional[str]
    confidence: float  # 0.0-1.0
    source: str  # Where names were found: "account_name", "category_names", "transaction_notes"

def _extract_names_from_account(
    self,
    account: AccountSummary,
    transactions: List[Dict[str, Any]],
    categories: List[CategorySummary]
) -> Optional[NameSuggestion]:
    """Extract person names from a specific account's data."""

    # 1. Try account name first
    names = self._parse_names_from_text(account.name)
    if len(names) == 2:
        return NameSuggestion(
            context="unknown",  # Will be set by caller
            person_1=names[0],
            person_2=names[1],
            confidence=0.9,
            source=f"account_name: {account.name}"
        )

    # 2. Try categories used in this account
    account_txns = [t for t in transactions if t.get("transaction_account", {}).get("id") == account.id]
    category_ids = {t.get("category", {}).get("id") for t in account_txns if t.get("category")}
    account_categories = [cat for cat in categories if cat.id in category_ids]

    for cat in account_categories:
        # Look for patterns like "Simon's Share", "Tori's Portion", etc.
        names = self._parse_names_from_text(cat.title)
        if len(names) >= 1:
            # Accumulate names across categories
            pass  # More complex logic here

    # 3. Try transaction payees/notes
    for txn in account_txns[:50]:  # Sample recent transactions
        payee = txn.get("payee", "")
        memo = txn.get("memo", "")
        # Look for patterns...

    return None

def _parse_names_from_text(self, text: str) -> List[str]:
    """Extract person names from text using patterns."""

    # Pattern 1: "Name1 & Name2" or "Name1 and Name2"
    pattern1 = r"([A-Z][a-z]+)\s+(?:&|and)\s+([A-Z][a-z]+)"
    match = re.search(pattern1, text)
    if match:
        return [match.group(1), match.group(2)]

    # Pattern 2: "Name1's" possessive form
    pattern2 = r"([A-Z][a-z]+)'s"
    matches = re.findall(pattern2, text)
    if matches:
        return list(set(matches))  # Deduplicate

    # Pattern 3: Just capitalized words (less confident)
    pattern3 = r"\b([A-Z][a-z]{2,})\b"
    matches = re.findall(pattern3, text)
    # Filter out common words
    common_words = {"Account", "Bills", "Shared", "Joint", "Kids", "Children", "Bank", "Card"}
    names = [m for m in matches if m not in common_words]

    return names[:2]  # Return max 2 names
```

### Phase 3: Update TemplateRecommendation

Add name suggestions to the recommendation:

```python
@dataclass
class TemplateRecommendation:
    """Recommended template combination for composable template system."""

    primary: str
    living: str
    additional: List[str]

    # NEW: Name suggestions for label customization
    name_suggestions: Dict[str, NameSuggestion] = field(default_factory=dict)
    # Keys: "shared-hybrid", "separated-parents"
```

### Phase 4: Update _recommend_template Method

Enhance the method to use account classification:

```python
def _recommend_template(
    self,
    accounts: List[AccountSummary],
    categories: List[CategorySummary],
    transactions: List[Dict[str, Any]]  # NEW parameter
) -> TemplateRecommendation:
    """Recommend templates based on account and category structure."""

    # ... existing PRIMARY template logic ...

    # NEW: Classify accounts
    account_classifications = self._classify_accounts(accounts, transactions)

    # Find household and parenting accounts
    household_accounts = [c for c in account_classifications if c.account_type == "household_shared"]
    parenting_accounts = [c for c in account_classifications if c.account_type == "parenting_shared"]

    # Determine LIVING template
    living_templates = []
    name_suggestions = {}

    if household_accounts:
        living_templates.append("shared-hybrid")
        # Extract names from household account
        for acc_class in household_accounts:
            account = next(a for a in accounts if a.id == acc_class.account_id)
            name_suggestion = self._extract_names_from_account(account, transactions, categories)
            if name_suggestion:
                name_suggestion.context = "shared-hybrid"
                name_suggestions["shared-hybrid"] = name_suggestion
                break

    if parenting_accounts:
        living_templates.append("separated-parents")
        # Extract names from parenting account
        for acc_class in parenting_accounts:
            account = next(a for a in accounts if a.id == acc_class.account_id)
            name_suggestion = self._extract_names_from_account(account, transactions, categories)
            if name_suggestion:
                name_suggestion.context = "separated-parents"
                name_suggestions["separated-parents"] = name_suggestion
                break

    if not living_templates:
        living_templates.append("single")

    # Use first template as primary, but track all detected
    living = living_templates[0]

    # ... existing ADDITIONAL template logic ...

    return TemplateRecommendation(
        primary=primary,
        living=living,
        additional=additional,
        name_suggestions=name_suggestions
    )
```

### Phase 5: Update install.md for Interactive Account Selection

Modify the onboarding command to show detected accounts and let users confirm or choose different ones:

```markdown
**Step 3d: Configure Template Labels (if applicable)**

For templates with configurable labels, show detected accounts and extract names:

**If Shared Hybrid selected:**
```bash
echo ""
echo "=== Household Shared Account Selection ==="

# Show detected household account(s)
if has_household_accounts:
    echo ""
    echo "I detected these potential household shared accounts:"
    echo ""
    for i, account in enumerate(household_accounts):
        echo "  $((i+1)). ${account.name} (${account.institution})"
        echo "      Confidence: ${account.confidence * 100}%"
        echo "      Why: ${account.indicators}"
        echo ""

    # Ask user to confirm or select different account
    read -p "Select household account (1-${#household_accounts[@]}) or 'o' for other: " choice

    if [[ "$choice" == "o" ]]; then
        # Show all accounts for manual selection
        echo ""
        echo "All accounts:"
        for i, account in enumerate(all_accounts):
            echo "  $((i+1)). ${account.name} (${account.institution})"
        read -p "Select account (1-${#all_accounts[@]}): " choice
        selected_account="${all_accounts[$((choice-1))]}"
    else
        selected_account="${household_accounts[$((choice-1))]}"
    fi
else
    # No household account detected - show all and ask user to pick
    echo "No household shared account detected."
    echo ""
    echo "Please select which account is used for household expenses:"
    for i, account in enumerate(all_accounts):
        echo "  $((i+1)). ${account.name} (${account.institution})"
    read -p "Select account (1-${#all_accounts[@]}) or 'n' for none: " choice

    if [[ "$choice" != "n" ]]; then
        selected_account="${all_accounts[$((choice-1))]}"
    fi
fi

# Extract names from the selected account
if [[ -n "$selected_account" ]]; then
    echo ""
    echo "Analyzing '${selected_account.name}' for contributor names..."
    name_suggestion=$(extract_names_from_account "$selected_account")

    if [[ -n "$name_suggestion" ]]; then
        CONTRIBUTOR_1="${name_suggestion.person_1}"
        CONTRIBUTOR_2="${name_suggestion.person_2}"
        echo ""
        echo "✓ Detected contributors: $CONTRIBUTOR_1 and $CONTRIBUTOR_2"
        echo "  Source: ${name_suggestion.source}"
        echo ""
        read -p "Use these names? (y/n): " confirm

        if [[ "$confirm" != "y" ]]; then
            read -p "Contributor 1 name: " CONTRIBUTOR_1
            read -p "Contributor 2 name: " CONTRIBUTOR_2
        fi
    else
        echo ""
        echo "Could not detect names from account. Please enter manually:"
        read -p "Contributor 1 name (e.g., Alex): " CONTRIBUTOR_1
        read -p "Contributor 2 name (e.g., Jordan): " CONTRIBUTOR_2
    fi
fi
```

**If Separated Parents selected:**
```bash
echo ""
echo "=== Parenting Shared Account Selection ==="

# Show detected parenting account(s)
if has_parenting_accounts:
    echo ""
    echo "I detected these potential parenting/custody accounts:"
    echo ""
    for i, account in enumerate(parenting_accounts):
        echo "  $((i+1)). ${account.name} (${account.institution})"
        echo "      Confidence: ${account.confidence * 100}%"
        echo "      Why: ${account.indicators}"
        echo ""

    read -p "Select parenting account (1-${#parenting_accounts[@]}) or 'o' for other: " choice

    if [[ "$choice" == "o" ]]; then
        # Show all accounts for manual selection
        echo ""
        echo "All accounts:"
        for i, account in enumerate(all_accounts):
            echo "  $((i+1)). ${account.name} (${account.institution})"
        read -p "Select account (1-${#all_accounts[@]}): " choice
        selected_account="${all_accounts[$((choice-1))]}"
    else
        selected_account="${parenting_accounts[$((choice-1))]}"
    fi
else
    # No parenting account detected - show all and ask user to pick
    echo "No parenting/custody account detected."
    echo ""
    echo "Please select which account is used for child-related expenses:"
    for i, account in enumerate(all_accounts):
        echo "  $((i+1)). ${account.name} (${account.institution})"
    read -p "Select account (1-${#all_accounts[@]}) or 'n' for none: " choice

    if [[ "$choice" != "n" ]]; then
        selected_account="${all_accounts[$((choice-1))]}"
    fi
fi

# Extract names from the selected parenting account
if [[ -n "$selected_account" ]]; then
    echo ""
    echo "Analyzing '${selected_account.name}' for parent names..."
    name_suggestion=$(extract_names_from_account "$selected_account")

    if [[ -n "$name_suggestion" ]]; then
        PARENT_1="${name_suggestion.person_1}"
        PARENT_2="${name_suggestion.person_2}"
        echo ""
        echo "✓ Detected parents: $PARENT_1 and $PARENT_2"
        echo "  Source: ${name_suggestion.source}"
        echo ""
        read -p "Use these names? (y/n): " confirm

        if [[ "$confirm" != "y" ]]; then
            read -p "Parent 1 name: " PARENT_1
            read -p "Parent 2 name: " PARENT_2
        fi
    else
        echo ""
        echo "Could not detect names from account. Please enter manually:"
        read -p "Parent 1 name (e.g., Sarah): " PARENT_1
        read -p "Parent 2 name (e.g., David): " PARENT_2
    fi
fi
```

**Save selected accounts to config:**
```bash
# Save account selections to template_config.json
echo "{
  \"primary\": \"$PRIMARY_TEMPLATE\",
  \"living\": [\"$LIVING_TEMPLATES\"],
  \"additional\": [\"$ADDITIONAL_TEMPLATES\"],
  \"labels\": {
    \"shared-hybrid\": {
      \"contributor_1\": \"$CONTRIBUTOR_1\",
      \"contributor_2\": \"$CONTRIBUTOR_2\",
      \"account_id\": \"${household_account.id}\",
      \"account_name\": \"${household_account.name}\"
    },
    \"separated-parents\": {
      \"parent_1\": \"$PARENT_1\",
      \"parent_2\": \"$PARENT_2\",
      \"account_id\": \"${parenting_account.id}\",
      \"account_name\": \"${parenting_account.name}\"
    }
  }
}" > data/template_config.json
```

## User Experience Flow

Here's what the user will see during onboarding with the new interactive account selection:

```
=== Household Shared Account Selection ===

I detected these potential household shared accounts:

  1. Shared Bills - Simon & Caitlin (Macquarie Bank)
      Confidence: 90%
      Why: Keywords in account name: "shared", name pattern detected

  2. Joint Savings (Westpac)
      Confidence: 70%
      Why: Keywords in account name: "joint"

Select household account (1-2) or 'o' for other: 1

Analyzing 'Shared Bills - Simon & Caitlin' for contributor names...

✓ Detected contributors: Simon and Caitlin
  Source: account_name (confidence: 0.9)

Use these names? (y/n): y

───────────────────────────────────────────────────────────

=== Parenting Shared Account Selection ===

I detected these potential parenting/custody accounts:

  1. Kids Account (Westpac)
      Confidence: 80%
      Why: Keywords in account name: "kids", categories: child support, school fees

Select parenting account (1) or 'o' for other: 1

Analyzing 'Kids Account' for parent names...

✓ Detected parents: Simon and Tori
  Source: category_names (Simon's Share, Tori's Share)

Use these names? (y/n): y

───────────────────────────────────────────────────────────

Configuration saved:
  • Household account: Shared Bills - Simon & Caitlin
    Contributors: Simon and Caitlin

  • Parenting account: Kids Account
    Parents: Simon and Tori
```

## Enhanced Discovery Report Structure

Update `DiscoveryReport` to include account classifications:

```python
@dataclass
class DiscoveryReport:
    """Complete discovery report for onboarding."""

    user_id: int
    user_email: str
    accounts: List[AccountSummary]
    categories: List[CategorySummary]
    transactions: TransactionSummary
    baseline_health_score: Optional[int]
    recommendation: TemplateRecommendation

    # NEW: Account classifications for interactive selection
    account_classifications: List[AccountClassification] = field(default_factory=list)
```

This allows the onboarding workflow to access:
- `report.account_classifications` - All accounts with their types and confidence
- `report.recommendation.name_suggestions` - Suggested names per context

## Implementation Note: Use AskUserQuestion Instead of Bash

Since the onboarding runs in Claude Code (not a terminal), we should use **AskUserQuestion** tool instead of bash `read` for interactive prompts:

```python
# In install.md command implementation

# Get household account classifications
household_accounts = [acc for acc in report.account_classifications
                      if acc.account_type == "household_shared"]

if household_accounts:
    # Build options for AskUserQuestion
    options = []
    for acc in household_accounts:
        options.append({
            "label": f"{acc.account_name} ({acc.institution})",
            "description": f"Confidence: {acc.confidence*100:.0f}% - {', '.join(acc.indicators)}"
        })

    # Add "Other account" option
    options.append({
        "label": "Other account",
        "description": "Choose a different account from the full list"
    })

    # Ask user to select
    response = AskUserQuestion(
        questions=[{
            "question": "Which account do you use for household shared expenses?",
            "header": "Household Acct",
            "options": options,
            "multiSelect": false
        }]
    )

    if response == "Other account":
        # Show all accounts...
        pass
    else:
        # Use selected account for name extraction
        selected_account = household_accounts[selected_index]
```

## Testing Strategy

### Test Case 1: Household Only
**Setup:**
- Account: "Shared Bills - Simon & Caitlin"
- No parenting accounts

**Expected:**
- Template: `shared-hybrid`
- Name suggestion: Simon, Caitlin
- Confidence: High (0.9)
- Source: "account_name: Shared Bills - Simon & Caitlin"

### Test Case 2: Parenting Only
**Setup:**
- Account: "Kids Account"
- Categories: "Simon's Share", "Tori's Share"

**Expected:**
- Template: `separated-parents`
- Name suggestion: Simon, Tori
- Confidence: Medium (0.7)
- Source: "category_names: Simon's Share, Tori's Share"

### Test Case 3: Both Contexts (User's Scenario)
**Setup:**
- Account 1: "Shared Bills - Simon & Caitlin"
- Account 2: "Kids Account" with categories "Simon's Share", "Tori's Share"

**Expected:**
- Templates: `shared-hybrid` + `separated-parents`
- Name suggestions:
  - shared-hybrid: Simon, Caitlin (confidence: 0.9, source: account_name)
  - separated-parents: Simon, Tori (confidence: 0.7, source: category_names)

### Test Case 4: Ambiguous/No Names
**Setup:**
- Account: "Joint Account"
- No categories with names

**Expected:**
- Template: `shared-hybrid`
- Name suggestion: None (fallback to manual input)

## Implementation Checklist

**Discovery Logic (discovery.py):**
- [ ] Add `AccountClassification` dataclass
- [ ] Add `NameSuggestion` dataclass
- [ ] Implement `_classify_accounts()` method
- [ ] Implement `_extract_names_from_account()` method
- [ ] Implement `_parse_names_from_text()` method with regex patterns
- [ ] Update `TemplateRecommendation` with `name_suggestions` field
- [ ] Update `DiscoveryReport` with `account_classifications` field
- [ ] Update `_recommend_template()` to pass transactions and use classification
- [ ] Update `analyze()` to pass transactions to `_recommend_template()`

**Onboarding Command (install.md):**
- [ ] Update `run_agent_smith()` to use `env -u VIRTUAL_ENV`
- [ ] Add interactive account selection for household accounts
- [ ] Add interactive account selection for parenting accounts
- [ ] Extract names from selected accounts (not globally)
- [ ] Use `AskUserQuestion` for account selection
- [ ] Save `account_id` and `account_name` to template_config.json

**Testing:**
- [ ] Write unit tests for `_classify_accounts()`
- [ ] Write unit tests for `_extract_names_from_account()`
- [ ] Write unit tests for `_parse_names_from_text()`
- [ ] Test with real account data (user's scenario)
- [ ] Integration test: full onboarding flow

**Documentation:**
- [ ] Update SKILL.md with new discovery features
- [ ] Add examples to onboarding-guide.md
- [ ] Update CHANGELOG.md

## Virtual Environment Issue

**Problem:** Warning when user has another project's venv active:
```
warning: `VIRTUAL_ENV=/home/slamb2k/Downloads/planets/.venv` does not match the project environment path `.venv`
```

**Solution:** Update `run_agent_smith()` helper to automatically ignore conflicting venvs:

```bash
# In agent-smith-plugin/commands/install.md

run_agent_smith() {
    local script_path="$1"
    shift

    if [ -n "${CLAUDE_PLUGIN_ROOT}" ]; then
        local skill_dir="${CLAUDE_PLUGIN_ROOT}/skills/agent-smith"
        local user_cwd="$(pwd)"

        if [ ! -d "$skill_dir" ]; then
            echo "Error: Agent Smith skill directory not found: $skill_dir"
            return 1
        fi

        # Run with VIRTUAL_ENV unset to avoid conflicts
        # uv will use the plugin's .venv automatically
        (cd "$skill_dir" && \
         USER_CWD="$user_cwd" \
         env -u VIRTUAL_ENV -u VIRTUAL_ENV_PROMPT \
         uv run python -u "scripts/$script_path" "$@")
    elif [ -f "./scripts/$script_path" ]; then
        # Development mode
        uv run python -u "./scripts/$script_path" "$@"
    else
        echo "Error: Agent Smith script not found: $script_path"
        return 1
    fi
}
```

**Why this approach is better:**
- ✅ Automatically ignores conflicting venvs (no user action needed)
- ✅ No warnings from uv about VIRTUAL_ENV mismatch
- ✅ Works transparently - user doesn't see the problem
- ✅ Uses `env -u` to unset vars only for the plugin's execution
- ✅ User's shell environment remains unchanged

**Alternative: Interactive venv handling (if transparency isn't desired)**

If you want to inform the user and let them choose:

```markdown
### Stage 1: Welcome & Prerequisites Check

1. Check for conflicting virtual environments:

if [ -n "$VIRTUAL_ENV" ]; then
    echo "⚠️  Another virtual environment is active:"
    echo "    $VIRTUAL_ENV"
    echo ""
    echo "Agent Smith will automatically use its own environment."
    echo "The active venv will be ignored during installation."
    echo ""
    # Use AskUserQuestion to let user decide
    response = AskUserQuestion(
        questions=[{
            "question": "Would you like to deactivate the conflicting venv?",
            "header": "Venv Detected",
            "options": [
                {
                    "label": "Deactivate it",
                    "description": "Deactivate $VIRTUAL_ENV and proceed cleanly"
                },
                {
                    "label": "Leave it active",
                    "description": "Agent Smith will ignore it automatically"
                }
            ],
            "multiSelect": false
        }]
    )

    if [ "$response" == "Deactivate it" ]; then
        unset VIRTUAL_ENV
        unset VIRTUAL_ENV_PROMPT
        export PATH=$(echo $PATH | tr ':' '\n' | grep -v "$VIRTUAL_ENV" | tr '\n' ':' | sed 's/:$//')
        echo "✓ Deactivated $VIRTUAL_ENV"
    else
        echo "✓ Proceeding with automatic venv isolation"
    fi
fi
```

2. Verify Agent Smith plugin installed
3. Check for .env file with API key
```

**Recommendation:** Use the transparent approach (update `run_agent_smith()`) rather than prompting the user. It's simpler and the user doesn't need to know about the internal venv handling.

---

## Summary of Enhancements

### 1. Smart Account Classification
- Automatically detect household vs parenting shared accounts
- Provide confidence scores and reasoning
- Support fallback to manual selection

### 2. Interactive Account Selection
- Show detected accounts with confidence scores
- Let users confirm or choose different accounts
- Handle edge cases (no detection, multiple matches)

### 3. Context-Specific Name Extraction
- Extract names from **selected account** only (not globally)
- Use multiple strategies: account names, categories, transactions
- Return different names for household vs parenting contexts

### 4. Transparent UX
- Show user what was detected and why
- Always allow user override
- Save account selections to config for future reference

### 5. Virtual Environment Check
- Detect conflicting venvs during installation
- Warn user and suggest deactivation
- Prevent confusion during onboarding

## Implementation Priority

**Phase 1 (High Priority):**
1. ✅ Design complete (this document)
2. Implement account classification logic
3. Implement name extraction logic
4. Update DiscoveryReport structure

**Phase 2 (Medium Priority):**
5. Update install.md with interactive account selection
6. Add venv conflict check
7. Write unit tests

**Phase 3 (Testing):**
8. Test with real account data
9. Validate name extraction accuracy
10. User acceptance testing

## Files to Modify

1. **`scripts/onboarding/discovery.py`**
   - Add `AccountClassification` dataclass
   - Add `NameSuggestion` dataclass
   - Add `_classify_accounts()` method
   - Add `_extract_names_from_account()` method
   - Add `_parse_names_from_text()` method
   - Update `TemplateRecommendation` with `name_suggestions`
   - Update `DiscoveryReport` with `account_classifications`
   - Update `_recommend_template()` to classify accounts
   - Update `analyze()` to populate classifications

2. **`agent-smith-plugin/commands/install.md`**
   - Add venv conflict check to Stage 1
   - Update Step 3d with interactive account selection
   - Use AskUserQuestion for account selection
   - Extract names from selected accounts
   - Save account_id to template_config.json

3. **Copy changes to plugin**:
   - `agent-smith-plugin/skills/agent-smith/scripts/onboarding/discovery.py`

4. **Tests**:
   - `tests/unit/test_discovery.py` - Add tests for new methods
   - `tests/integration/test_onboarding.py` - Test full flow

## Estimated Effort

- Discovery logic implementation: **3-4 hours**
- Install.md updates: **2 hours**
- Testing: **2 hours**
- Documentation: **1 hour**

**Total: 8-9 hours**
