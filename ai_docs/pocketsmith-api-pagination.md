---
title: PocketSmith API Pagination
category: ai_docs
status: active
created: 2025-11-27
last_updated: 2025-11-27
tags: [pocketsmith, api, pagination, collections]
source: https://developers.pocketsmith.com/docs/pagination
---

# PocketSmith API Pagination

The PocketSmith API leverages pagination for collections that are likely to be large in size, such as transactions. This means that it's not possible to request the whole collection at once, you must instead ask the API for a certain page of results.

## Response Headers

You can identify if a collection is being paginated by the presence of the following headers:

| Header | Description | Example |
|--------|-------------|---------|
| `Per-Page` | How many results from the collection are on each page | 30 |
| `Total` | How many total records there are across all pages | 432 |
| `Link` | An [RFC 5988](https://tools.ietf.org/html/rfc5988)-compliant header with links to get to the first, last, next and previous pages | See below |

## The Link Header

The `Link` header provides navigation URLs for paginated results:

```
Link: <https://api.pocketsmith.com/v2/users/18609/transactions?end_date=2015-06-01&page=1&start_date=2011-01-01>; rel="first",
      <https://api.pocketsmith.com/v2/users/18609/transactions?end_date=2015-06-01&page=12&start_date=2011-01-01>; rel="last",
      <https://api.pocketsmith.com/v2/users/18609/transactions?end_date=2015-06-01&page=11&start_date=2011-01-01>; rel="next",
      <https://api.pocketsmith.com/v2/users/18609/transactions?end_date=2015-06-01&page=9&start_date=2011-01-01>; rel="prev"
```

The header contains links with the following `rel` values:
- `first` - URL to the first page
- `last` - URL to the last page
- `next` - URL to the next page (if available)
- `prev` - URL to the previous page (if available)

## Navigating Pages

By default, you will be delivered the first page (page **1**) of results. You can request specific pages using the `page` URL parameter:

```
GET /v2/users/{id}/transactions?page=3
```

It is recommended to leverage the `Link` header when navigating between pages.

## Adjusting the Page Size

The default number of records per page is 30, but you can change this as needed:

| Parameter | Default | Minimum | Maximum |
|-----------|---------|---------|---------|
| `per_page` | 30 | 10 | 1000 |

Example:
```
GET /v2/users/{id}/transactions?page=3&per_page=500
```

**Note:** Unless the total size of the collection fits exactly into pages of size *n*, the last page will have fewer results than the others.

## Link Header Parsing Libraries

There are plenty of libraries available across languages which can parse compliant Link headers into a data structure:

- [parse-link-header](https://github.com/thlorenz/parse-link-header) for JavaScript
- [link_header](https://github.com/asplake/link_header) for Ruby
- [link-rel-parser-php](https://github.com/indieweb/link-rel-parser-php) for PHP

## Example: Fetching All Transactions (Python)

```python
import requests
from urllib.parse import parse_qs, urlparse

def fetch_all_transactions(user_id, api_key):
    """Fetch all transactions using pagination."""
    base_url = f"https://api.pocketsmith.com/v2/users/{user_id}/transactions"
    headers = {"X-Developer-Key": api_key}
    params = {"per_page": 1000}  # Use max page size for efficiency

    all_transactions = []
    url = base_url

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        transactions = response.json()
        all_transactions.extend(transactions)

        # Parse Link header for next page
        link_header = response.headers.get("Link", "")
        url = get_next_url(link_header)
        params = {}  # Next URL has params already

    return all_transactions

def get_next_url(link_header):
    """Extract 'next' URL from Link header."""
    if not link_header:
        return None

    for part in link_header.split(","):
        if 'rel="next"' in part:
            url = part.split(";")[0].strip().strip("<>")
            return url
    return None
```

## Best Practices

1. **Use Maximum Page Size** - For bulk operations, use `per_page=1000` to minimize API calls.

2. **Use Link Headers** - Parse the `Link` header rather than manually constructing URLs.

3. **Check Total Count** - Use the `Total` header to estimate progress and time remaining.

4. **Handle Empty Pages** - The last page may have fewer results; don't assume all pages are full.

5. **Respect Rate Limits** - Even with pagination, respect rate limits when fetching large datasets.
