---
title: PocketSmith API Error Handling
category: ai_docs
status: active
created: 2025-11-27
last_updated: 2025-11-27
tags: [pocketsmith, api, errors, http-status]
source: https://developers.pocketsmith.com/docs/errors
---

# PocketSmith API Error Handling

The PocketSmith API provides proper HTTP status codes when errors happen. This helps inform the client of the nature of the error without having to examine the response body, which will contain an English error message.

## Error Types

| Name | HTTP Status Code | Meaning | What You Should Do |
|------|------------------|---------|-------------------|
| Bad Request | 400 | The request was invalid or malformed | From the error message, find out what was wrong with your request |
| Unauthorized | 401 | The access token was missing or invalid | Obtain a new access token with OAuth, potentially refreshing your token if it had expired |
| Not Allowed | 403 | Not allowed to perform the action, usually due to lack of permission to read or modify the requested resource | Check permissions and scope |
| Not Found | 404 | The requested resource was not found | Consider the resource to be non-existent, it either never existed or no longer exists |
| Method Not Allowed | 405 | The requested resource was valid, but not for the HTTP verb used | Use the correct HTTP method (GET, POST, PUT, DELETE) |
| Unprocessable Entity | 422 | A validation error occurred | See which field failed validation and remedy the issue. If the data was user-provided, show them the error and have them fix the data |
| Internal Server Error | 500 | Something broke on PocketSmith's side | They've been alerted to the problem and will be looking into it |
| Service Unavailable | 503 | PocketSmith or a dependency are down temporarily for maintenance | Try the request again at a later time |

## Error Response Format

Every error listed above will have a JSON response body in the form:

```json
{
  "error": "A nice English error message explaining the problem"
}
```

## OAuth Errors

Errors arising from OAuth will be spec-compliant, which means both an `error` and `error_description` field will be present in the response.

- `error` - An identifier like `invalid_credentials`
- `error_description` - An English explanation of the issue

To know if you're getting an error in OAuth format or a regular PocketSmith error, check for the presence of the `error_description` field.

Example OAuth error response:
```json
{
  "error": "invalid_credentials",
  "error_description": "The provided credentials are not valid"
}
```

## Best Practices for Error Handling

### 1. Check HTTP Status First
Always check the HTTP status code before parsing the response body.

### 2. Parse Error Messages
Extract and display the `error` field to understand what went wrong.

### 3. Handle Rate Limiting (429)
When you receive a 429 status, check the `X-RateLimit-Reset` header to know when to retry.

### 4. Retry Transient Errors
For 500 and 503 errors, implement exponential backoff and retry logic.

### 5. Validate Before Sending
For 422 errors, validate data client-side before sending to avoid unnecessary API calls.

## Example Error Handling (Python)

```python
import requests

def handle_response(response):
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        # Token expired - refresh and retry
        refresh_token()
        raise AuthenticationError("Token expired")
    elif response.status_code == 404:
        raise NotFoundError("Resource not found")
    elif response.status_code == 422:
        error_msg = response.json().get("error", "Validation error")
        raise ValidationError(error_msg)
    elif response.status_code == 429:
        reset_time = response.headers.get("X-RateLimit-Reset")
        raise RateLimitError(f"Rate limited. Reset at {reset_time}")
    else:
        error_msg = response.json().get("error", "Unknown error")
        raise APIError(f"API error: {error_msg}")
```
