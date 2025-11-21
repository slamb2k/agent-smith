# Health Check System - Index

**Last Updated:** 2025-11-21

**Purpose:** Health check scoring, recommendations, and monitoring for PocketSmith setups

---

## Core Modules

| File | Description | Status |
|------|-------------|--------|
| `__init__.py` | Module exports | ✓ Implemented |
| `scores.py` | Health scorers (6 dimensions) | ✓ Implemented |
| `engine.py` | HealthCheckEngine orchestration | ✓ Implemented |
| `collector.py` | Data collection from API | ✓ Implemented |
| `recommendations.py` | RecommendationEngine | ✓ Implemented |
| `monitoring.py` | Automated health monitoring | ✓ Implemented |

---

## Health Scorers (scores.py)

Six dimension scorers with weighted scoring:

| Scorer | Weight | Metrics |
|--------|--------|---------|
| DataQualityScorer | 25% | Uncategorized rate, duplicates, gaps |
| CategoryStructureScorer | 20% | Depth, unused categories, distribution |
| RuleEngineScorer | 15% | Coverage, efficiency, conflicts |
| TaxReadinessScorer | 15% | Tax categorization, compliance |
| AutomationScorer | 10% | Savings automation, bill scheduling |
| BudgetAlignmentScorer | 15% | Variance, overspending |

---

## Key Classes

**scores.py:**
- `HealthStatus` - Enum (PASS, WARN, FAIL)
- `HealthScore` - Dataclass with score, status, metrics, recommendations
- `BaseScorer` - Abstract base class for all scorers

**engine.py:**
- `HealthCheckResult` - Complete health check result
- `HealthCheckEngine` - Runs all scorers, calculates overall score

**collector.py:**
- `HealthDataCollector` - Gathers data from PocketSmith API

**recommendations.py:**
- `Recommendation` - Dataclass with priority, effort, command
- `RecommendationEngine` - Generates prioritized recommendations

**monitoring.py:**
- `MonitoringConfig` - Monitoring settings
- `HealthAlert` - Alert dataclass
- `HealthMonitor` - Automated monitoring with alerts

---

## Tests

- `tests/unit/test_health_scores.py` - 36 unit tests
- `tests/unit/test_health_engine.py` - 4 unit tests
- `tests/unit/test_health_collector.py` - 3 unit tests
- `tests/unit/test_recommendations.py` - 4 unit tests
- `tests/unit/test_health_monitoring.py` - 5 unit tests
- `tests/integration/test_health_check.py` - 3 integration tests

---

## Related Documentation

- **User Guide:** [../../docs/guides/health-check-guide.md](../../docs/guides/health-check-guide.md)
- **Data Directory:** [../../data/health/INDEX.md](../../data/health/INDEX.md)

---

**Status:** Complete
