# Health Check Data

## Purpose
Stores health check results, historical scores, and recommendations.

## Files
- `health_scores.json` - Latest health scores for each dimension
- `health_history.json` - Historical health check results
- `recommendations.json` - Current active recommendations

## Retention
- Current scores: Always kept
- History: 90 days, then archived monthly
