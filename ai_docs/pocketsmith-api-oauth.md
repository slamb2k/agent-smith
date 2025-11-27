---
title: PocketSmith API OAuth 2.0 Guide
category: ai_docs
status: active
created: 2025-11-27
last_updated: 2025-11-27
tags: [pocketsmith, api, oauth, authentication, authorization]
source: https://developers.pocketsmith.com/docs/oauth
---

# PocketSmith API OAuth 2.0 Guide

The PocketSmith API uses the OAuth 2 standard for authorization. This allows users to delegate third parties discrete access to their PocketSmith account.

## OAuth Endpoints

| Endpoint | URL |
|----------|-----|
| Authorization URL | `https://my.pocketsmith.com/oauth/authorize` |
| Access Token URL | `https://api.pocketsmith.com/v2/oauth/access_token` |

## Client Credentials

Before you can use OAuth, you must register your application with PocketSmith and obtain your `client_id` and `client_secret`. These are used to identify your application when making requests to the OAuth API endpoints.

Contact PocketSmith to register your app and get credentials.

## Third-Party OAuth Libraries

Existing OAuth 2 client libraries:

- [thephpleague/oauth2-client](https://github.com/thephpleague/oauth2-client) for PHP
- [intridea/oauth2](https://github.com/intridea/oauth2) for Ruby
- [ciaranj/node-oauth](https://github.com/ciaranj/node-oauth) for Node
- [DotNetOpenAuth](https://github.com/DotNetOpenAuth/DotNetOpenAuth) for .NET

## Authorization Code Flow

### Step 1: Redirect User for Authorization

Redirect the user to the PocketSmith authorization page:

```
https://my.pocketsmith.com/oauth/authorize
```

**Query Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `response_type` | string | Must be `code` |
| `client_id` | string | Your client/application ID |
| `scope` | string | Space-delimited string of scopes to request |
| `redirect_uri` | string | URI to redirect user back to (must be registered) |
| `state` | string | Optional state string to prevent CSRF attacks |

### Step 2: Handle the Returning User

The user will be redirected back to your `redirect_uri` with either:
- **Success:** `?code=AUTHORIZATION_CODE` - Use this to get access token
- **Denied:** `?error=access_denied` - User denied access

### Step 3: Exchange Code for Access Token

Make a POST request to get the access token:

```
POST https://api.pocketsmith.com/v2/oauth/access_token
```

**Request Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `grant_type` | string | Must be `authorization_code` |
| `client_id` | string | Your client/application ID |
| `client_secret` | string | Your client/application secret |
| `redirect_uri` | string | Same redirect URI used in authorization step |
| `code` | string | The authorization code from user return |

### Step 4: Use the Access Token

Include the token in API requests:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Available Scopes

| Scope | Description |
|-------|-------------|
| `user.read` | Access user's details and preferences |
| `user.write` | Change user's details and preferences |
| `accounts.read` | List and view transaction accounts |
| `accounts.write` | Update and delete transaction accounts |
| `transactions.read` | List and view accounts and transactions |
| `transactions.write` | Create, update and delete transactions |
| `categories.read` | View categories |
| `categories.write` | Edit and delete categories |
| `budget` | Analyse budgets and trends |

**Note:** If requesting scopes already approved, the user won't be prompted again.

## Refreshing Access Tokens

Access tokens have a lifetime of **1 hour (3600 seconds)**. After expiration, use the refresh token to get a new access token.

### Refresh Token Request

```
POST https://api.pocketsmith.com/v2/oauth/access_token
```

**Request Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `grant_type` | string | Must be `refresh_token` |
| `client_id` | string | Your client/application ID |
| `client_secret` | string | Your client/application secret |
| `refresh_token` | string | The refresh token |
| `scope` | string | Optional: space-delimited scopes to de-escalate |

### Scope Escalation/De-escalation

When refreshing, you can:
- **De-escalate:** Request fewer scopes than originally granted
- **Escalate:** Only to scopes originally approved by the user

## Implicit Flow

For client-side applications (e.g., JavaScript) that cannot keep secrets private.

### Differences from Authorization Code Flow

1. Use `response_type=token` instead of `response_type=code`
2. Access token returned directly in the redirect URL fragment:
   ```
   https://your.app/callback#access_token=0ab61721b9a...&expires_in=3600&token_type=Bearer
   ```
3. **No refresh token is provided** - redirect user for re-authorization when token expires

## Example: Authorization Code Flow (Python)

```python
import requests
from urllib.parse import urlencode

CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
REDIRECT_URI = "https://your.app/callback"

def get_authorization_url(scopes, state=None):
    """Generate the authorization URL for user redirect."""
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": " ".join(scopes),
        "redirect_uri": REDIRECT_URI,
    }
    if state:
        params["state"] = state

    return f"https://my.pocketsmith.com/oauth/authorize?{urlencode(params)}"

def exchange_code_for_token(authorization_code):
    """Exchange authorization code for access token."""
    response = requests.post(
        "https://api.pocketsmith.com/v2/oauth/access_token",
        data={
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": authorization_code,
        }
    )
    response.raise_for_status()
    return response.json()

def refresh_access_token(refresh_token, scopes=None):
    """Refresh an expired access token."""
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    if scopes:
        data["scope"] = " ".join(scopes)

    response = requests.post(
        "https://api.pocketsmith.com/v2/oauth/access_token",
        data=data
    )
    response.raise_for_status()
    return response.json()
```

## Security Best Practices

1. **Store secrets securely** - Never expose `client_secret` in client-side code
2. **Use state parameter** - Prevent CSRF attacks by validating state on return
3. **Validate redirect URIs** - Only accept redirects to registered URIs
4. **Refresh tokens proactively** - Refresh before expiration to avoid interruptions
5. **Request minimal scopes** - Only request the scopes your app actually needs
