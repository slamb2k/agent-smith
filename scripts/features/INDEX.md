# scripts/features/INDEX.md

**Directory:** Phase 7 advanced features modules
**Purpose:** Smart alerts, merchant intelligence, document management, multi-user support, benchmarking, and audit trail

---

## Files

### `alerts.py` (237 lines)
**Smart alerts and notification scheduling**

**Classes:**
- `AlertType(Enum)` - Alert categories (budget, tax, pattern, optimization)
- `AlertSeverity(Enum)` - Severity levels (info, warning, critical)
- `Alert` - Alert dataclass with acknowledgment
- `ScheduleType(Enum)` - Schedule frequencies (weekly, monthly, quarterly, annual, one-time)
- `AlertSchedule` - Scheduled alert with due checking
- `AlertEngine` - Alert creation and management
- `AlertScheduler` - Schedule management and processing

**Key Methods:**
```python
engine = AlertEngine(user_id="user_123")
alert = engine.create_alert(
    alert_type=AlertType.BUDGET,
    severity=AlertSeverity.WARNING,
    title="Budget Exceeded",
    message="Over budget by $50",
)

scheduler = AlertScheduler(alert_engine=engine)
schedule = scheduler.add_schedule(
    schedule_type=ScheduleType.WEEKLY,
    alert_type=AlertType.BUDGET,
    title="Weekly Review",
    next_run=datetime(2025, 11, 28, 9, 0),
)

due_alerts = scheduler.process_due_schedules()
```

**Tests:** `tests/unit/test_alerts.py` (8 tests), `tests/unit/test_alert_scheduler.py` (6 tests)

---

### `merchant_intelligence.py` (158 lines)
**Merchant variation detection and payee enrichment**

**Classes:**
- `MerchantGroup` - Group of related merchant name variations
- `MerchantMatcher` - Variation detection and grouping

**Key Methods:**
```python
matcher = MerchantMatcher()

# Normalize payee names (removes PTY LTD, transaction IDs, etc.)
normalized = matcher.normalize_payee("WOOLWORTHS PTY LTD")  # "woolworths"

# Add variation to group
matcher.add_variation("Woolworths", "WOOLWORTHS PTY LTD")

# Find canonical name
canonical = matcher.find_canonical("woolworth")  # "Woolworths"

# Suggest matches
suggestions = matcher.suggest_matches("woollies", threshold=0.8)
# Returns: [(canonical_name, similarity_score), ...]
```

**Features:**
- Payee normalization (remove suffixes, IDs, whitespace)
- Similarity calculation using `difflib.SequenceMatcher`
- Variation grouping with canonical names
- Match suggestions with configurable threshold

**Tests:** `tests/unit/test_merchant_intelligence.py` (6 tests)

---

### `documents.py` (162 lines)
**Document and receipt requirement tracking**

**Classes:**
- `DocumentRequirement(Enum)` - Requirement levels (required, recommended, optional)
- `DocumentStatus(Enum)` - Documentation status (missing, attached, verified)
- `TransactionDocument` - Documentation record for transaction
- `DocumentManager` - Requirement tracking and management

**Key Methods:**
```python
manager = DocumentManager()

# Track transaction (auto-determines requirement)
doc = manager.track_transaction(
    transaction_id=12345,
    amount=450.00,  # > $300 = REQUIRED
    category="Work Expenses",
    date=datetime(2025, 11, 15),
)

# Attach document
doc.attach_document("https://example.com/receipt.pdf")

# Get missing documents
missing = manager.get_missing_documents(required_only=True)
```

**ATO Rules:**
- `> $300`: REQUIRED (substantiation threshold)
- `> $100` in deductible categories: RECOMMENDED
- Otherwise: OPTIONAL

**Deductible Categories:** Work Expenses, Office Supplies, Professional Development, Business Travel, Home Office, Vehicle Expenses

**Tests:** `tests/unit/test_documents.py` (8 tests)

---

### `multi_user.py` (189 lines)
**Multi-user shared expense and settlement tracking**

**Classes:**
- `SharedExpense` - Shared expense with split calculation
- `Settlement` - Settlement payment between users
- `SharedExpenseTracker` - Balance and settlement management

**Key Methods:**
```python
tracker = SharedExpenseTracker(users=["alice", "bob", "charlie"])

# Add expense with equal split
expense = tracker.add_expense(
    transaction_id=1,
    amount=150.00,
    description="Dinner",
    paid_by="alice",
    date=datetime.now(),
    split_equally=True,
)

# Add expense with custom split
expense = tracker.add_expense(
    transaction_id=2,
    amount=120.00,
    description="Groceries",
    paid_by="bob",
    date=datetime.now(),
    split_ratios={"alice": 0.5, "bob": 0.25, "charlie": 0.25},
)

# Calculate balances
balances = tracker.calculate_balances()
# Returns: {"alice": 20.00, "bob": -10.00, "charlie": -10.00}

# Generate settlement recommendations
settlements = tracker.generate_settlements()
# Returns: [Settlement(from_user="bob", to_user="alice", amount=10.00), ...]
```

**Features:**
- Equal and custom ratio splitting
- Net balance calculation across all expenses
- Optimal settlement generation (minimize transactions)

**Tests:** `tests/unit/test_multi_user.py` (10 tests)

---

### `benchmarking.py` (135 lines)
**Privacy-first comparative benchmarking**

**Classes:**
- `PeerCriteria` - Criteria for peer group selection
- `BenchmarkResult` - Comparison result with statistics
- `BenchmarkEngine` - Anonymous peer comparison

**Key Methods:**
```python
engine = BenchmarkEngine()

criteria = PeerCriteria(
    household_size=2,
    income_bracket="50k-75k",
    location="Sydney",
)

# Add anonymized data point
engine.add_data_point(
    category="Groceries",
    amount=500.00,
    user_id="user_123",  # Anonymized via SHA-256
    criteria=criteria,
)

# Compare to peers
result = engine.compare(
    category="Groceries",
    user_amount=525.00,
    criteria=criteria,
)
# Returns: BenchmarkResult(
#   peer_average=500.0,
#   peer_median=500.0,
#   percentile=55,
#   peer_count=10
# )
```

**Privacy Features:**
- SHA-256 user ID anonymization
- Aggregated data only (no user linkage)
- Minimum 3 peers required for comparison

**Tests:** `tests/unit/test_benchmarking.py` (5 tests)

---

### `audit.py` (183 lines)
**Audit trail and activity logging**

**Classes:**
- `AuditAction(Enum)` - Auditable action types
- `AuditEntry` - Audit log entry with serialization
- `AuditLogger` - Activity logging and queries

**Key Methods:**
```python
logger = AuditLogger(user_id="user_123")

# Log action
entry = logger.log_action(
    action=AuditAction.TRANSACTION_MODIFY,
    description="Changed category",
    before_state={"category": "Food"},
    after_state={"category": "Groceries"},
    affected_ids=[123],
)

# Query entries
entries = logger.get_entries(
    action=AuditAction.TRANSACTION_MODIFY,
    affected_id=123,
    start_date=datetime(2025, 11, 1),
)

# Check undo capability
can_undo = logger.can_undo(entry.entry_id)  # True if has before_state

# Serialize for storage
data = entry.to_dict()
restored = AuditEntry.from_dict(data)
```

**Audit Actions:**
- Transaction: modify, delete
- Category: create, modify, delete
- Rule: create, modify, delete
- Bulk operation
- Report generation

**Features:**
- Before/after state tracking
- Undo capability detection
- Filtering by action, ID, date range
- JSON serialization

**Tests:** `tests/unit/test_audit.py` (9 tests)

---

## Usage Patterns

### Alert Workflow
1. Create `AlertEngine` for user
2. Create `AlertScheduler` with engine
3. Add schedules with `add_schedule()`
4. Periodically call `process_due_schedules()`
5. User acknowledges alerts with `alert.acknowledge()`

### Merchant Learning Workflow
1. Create `MerchantMatcher`
2. Process transactions, normalize payee names
3. Suggest matches for variations
4. User confirms/corrects canonical name
5. Add variation with `add_variation()`
6. Future transactions auto-matched

### Document Tracking Workflow
1. Create `DocumentManager`
2. Track transactions with `track_transaction()`
3. System determines requirement (ATO rules)
4. Query missing with `get_missing_documents()`
5. Attach receipts with `doc.attach_document()`

### Shared Expense Workflow
1. Create `SharedExpenseTracker` with users
2. Add expenses with `add_expense()`
3. Calculate balances with `calculate_balances()`
4. Generate settlements with `generate_settlements()`
5. Record payments, mark expenses as settled

### Benchmarking Workflow
1. Create `BenchmarkEngine`
2. Define `PeerCriteria`
3. Add data points with `add_data_point()` (anonymized)
4. Compare user with `compare()`
5. Present percentile and peer statistics

### Audit Trail Workflow
1. Create `AuditLogger` for user
2. Log all actions with `log_action()`
3. Include before/after state for undo
4. Query with `get_entries()` filters
5. Check undo capability with `can_undo()`

---

**Total Tests:** 52 unit tests across 6 feature modules
**Integration Tests:** 6 workflow tests in `tests/integration/test_advanced_features.py`

**Next Phase:** Phase 8 - Health Check & Polish
