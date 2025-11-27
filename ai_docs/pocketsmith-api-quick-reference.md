---
title: PocketSmith API Quick Reference
category: ai_docs
status: active
created: 2025-11-27
last_updated: 2025-11-27
tags: [pocketsmith, api, reference, endpoints]
source: https://developers.pocketsmith.com
---

# PocketSmith API Quick Reference

## Base Information

**Base URL:** `https://api.pocketsmith.com/v2`

**Authentication Methods:**
1. **Developer Key** (Personal use): Include `X-Developer-Key` header
2. **OAuth 2.0** (App development): Include `Authorization: Bearer {token}` header

**Common Headers:**
```
X-Developer-Key: YOUR_DEVELOPER_KEY
# OR
Authorization: Bearer YOUR_ACCESS_TOKEN

Content-Type: application/json
Accept: application/json
```

## Authentication

### Developer Key (Personal)
```bash
curl --header "X-Developer-Key: YOUR_KEY" \
     https://api.pocketsmith.com/v2/me
```

Get your developer key from: Settings > Security in PocketSmith

### OAuth 2.0 (Apps)
See [pocketsmith-api-oauth.md](pocketsmith-api-oauth.md) for complete integration details.

## Core Resources

### Users
- `GET /v2/me` - Get current user
- `GET /v2/users/{id}` - Get user by ID
- `PUT /v2/users/{id}` - Update user

### Accounts
- `GET /v2/accounts/{id}` - Get account details
- `GET /v2/users/{id}/accounts` - List user's accounts
- `PUT /v2/accounts/{id}` - Update account
- `DELETE /v2/accounts/{id}` - Delete account

### Transactions
- `GET /v2/transactions/{id}` - Get transaction
- `GET /v2/accounts/{id}/transactions` - List account transactions
- `GET /v2/users/{id}/transactions` - List user transactions
- `POST /v2/transaction_accounts/{id}/transactions` - Create transaction
- `PUT /v2/transactions/{id}` - Update transaction
- `DELETE /v2/transactions/{id}` - Delete transaction

### Categories
- `GET /v2/categories/{id}` - Get category
- `GET /v2/users/{id}/categories` - List user's categories
- `GET /v2/categories/{id}/transactions` - Get category transactions
- `POST /v2/users/{id}/categories` - Create category
- `PUT /v2/categories/{id}` - Update category
- `DELETE /v2/categories/{id}` - Delete category

### Budgets
- `GET /v2/users/{id}/budget` - Get budget overview
- `GET /v2/users/{id}/budget_summary` - Get budget summary
- `GET /v2/budget_analysis_packages/{id}` - Get budget analysis

### Transaction Accounts
- `GET /v2/transaction_accounts/{id}` - Get transaction account
- `GET /v2/users/{id}/transaction_accounts` - List user's transaction accounts
- `PUT /v2/transaction_accounts/{id}` - Update transaction account

### Institutions
- `GET /v2/institutions/{id}` - Get institution
- `GET /v2/institutions/{id}/accounts` - Get institution accounts
- `GET /v2/users/{id}/institutions` - List user's institutions
- `PUT /v2/institutions/{id}` - Update institution
- `DELETE /v2/institutions/{id}` - Delete institution

### Attachments
- `GET /v2/attachments/{id}` - Get attachment
- `GET /v2/users/{id}/attachments` - List user's attachments
- `GET /v2/transactions/{id}/attachments` - List transaction attachments
- `POST /v2/users/{id}/attachments` - Create attachment
- `POST /v2/transactions/{id}/attachments` - Attach to transaction
- `PUT /v2/attachments/{id}` - Update attachment
- `DELETE /v2/attachments/{id}` - Delete attachment

### Events (Forecasting)
- `GET /v2/events/{id}` - Get event
- `GET /v2/scenarios/{id}/events` - List scenario events
- `POST /v2/scenarios/{id}/events` - Create event
- `PUT /v2/events/{id}` - Update event
- `DELETE /v2/events/{id}` - Delete event

### Labels
- `GET /v2/users/{id}/labels` - List user's labels
- `POST /v2/users/{id}/labels` - Create label
- `PUT /v2/labels/{id}` - Update label
- `DELETE /v2/labels/{id}` - Delete label

### Time Zones & Currencies
- `GET /v2/time_zones` - List time zones
- `GET /v2/currencies` - List currencies
- `GET /v2/currencies/{id}` - Get currency

## Pagination

All list endpoints support pagination:
```
?page=1&per_page=50
```

Default: `page=1`, `per_page=30`
Maximum: `per_page=100` (can be up to 1000 for some endpoints)

Response headers include:
- `Link` - Pagination links (first, prev, next, last)
- `X-Total-Count` - Total number of items
- `Per-Page` - Items per page
- `Total` - Total records

## Common Query Parameters

### Dates
- `start_date` - ISO 8601 format: `2024-01-01`
- `end_date` - ISO 8601 format: `2024-12-31`

### Filtering Transactions
- `uncategorised=true` - Only uncategorised transactions
- `type=debit|credit` - Filter by transaction type
- `needs_review=true` - Transactions needing review
- `search=query` - Full-text search

### Sorting
- `sort=date` - Sort by field
- `order=asc|desc` - Sort order

## Error Handling

Standard HTTP status codes:
- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Unprocessable Entity
- `429` - Too Many Requests (Rate Limit)
- `500` - Internal Server Error

Error response format:
```json
{
  "error": "Error message here"
}
```

See [pocketsmith-api-errors.md](pocketsmith-api-errors.md) for details.

## Rate Limiting

The API implements rate limiting. Check response headers:
- `X-RateLimit-Limit` - Maximum requests per period
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Unix timestamp when limit resets

## Example: Complete Transaction Creation

```bash
curl -X POST https://api.pocketsmith.com/v2/transaction_accounts/{account_id}/transactions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payee": "Coffee Shop",
    "amount": -4.50,
    "date": "2024-01-15",
    "category_id": 123,
    "note": "Morning coffee"
  }'
```

## Example: Listing Transactions with Filters

```bash
curl -G https://api.pocketsmith.com/v2/users/{user_id}/transactions \
  -H "X-Developer-Key: YOUR_KEY" \
  --data-urlencode "start_date=2024-01-01" \
  --data-urlencode "end_date=2024-01-31" \
  --data-urlencode "search=coffee" \
  --data-urlencode "per_page=50"
```

## Tips for AI Agents

1. **Always include authentication** - Either developer key or OAuth token
2. **Use pagination** - For large result sets
3. **Check rate limits** - Respect API rate limits
4. **Handle errors gracefully** - Parse error messages
5. **Use correct HTTP methods** - GET for reading, POST for creating, PUT for updating, DELETE for removing
6. **Validate dates** - Use ISO 8601 format (YYYY-MM-DD)
7. **Include proper headers** - Content-Type and Accept headers

## Additional Resources

- [Full API Reference](https://developers.pocketsmith.com/)
- [OAuth Guide](pocketsmith-api-oauth.md)
- [Pagination Guide](pocketsmith-api-pagination.md)
- [Budgeting Guide](pocketsmith-api-budgeting.md)

## Official Links

- Developer Portal: https://developers.pocketsmith.com/
- API Status: https://status.pocketsmith.com/
- OpenAPI Spec: https://github.com/pocketsmith/api
