# PocketSmith API Documentation (Offline Reference)

**API Version:** v2.0
**Base URL:** `https://api.pocketsmith.com/v2`
**Documentation Source:** https://developers.pocketsmith.com/
**Last Updated:** 2025-11-16

---

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication](#authentication)
   - [Developer Keys](#developer-keys-personal-tools)
   - [OAuth 2.0](#oauth-20-multi-user-apps)
3. [API Reference](#api-reference)
   - [Users](#users)
   - [Institutions](#institutions)
   - [Accounts](#accounts)
   - [Transaction Accounts](#transaction-accounts)
   - [Transactions](#transactions)
   - [Categories](#categories)
   - [Budgeting](#budgeting)
   - [Supporting Resources](#supporting-resources)
4. [Common Topics](#common-topics)
   - [Pagination](#pagination)
   - [Error Handling](#error-handling)
5. [Changelog](#changelog)
6. [Support](#support)

---

## Introduction

The PocketSmith API is freely available to all developers without restrictions. The platform welcomes developers to build tools and integrations using their services.

**Developer Hub:** https://developers.pocketsmith.com/

---

## Authentication

PocketSmith provides two authentication methods depending on your use case.

### Developer Keys (Personal Tools)

For building personal tools like dashboard widgets or transaction importers, use developer keys.

**Configuration:**
- Manage keys in: Settings > Security within your PocketSmith account
- **Header:** `X-Developer-Key`
- **Access:** Persistent API access to your own account

**Example Request:**
```bash
curl --header "X-Developer-Key: YOUR_KEY_HERE" \
  https://api.pocketsmith.com/v2/me
```

**Supported Languages:**
- Shell (curl)
- Node.js
- JavaScript
- PHP
- Python

### OAuth 2.0 (Multi-User Apps)

To create applications that other PocketSmith users can access, you'll need to use OAuth 2.0.

**Setup Process:**

1. **Register your application** by contacting the team at [email protected]
2. **Provide details** about yourself and your planned integration
3. **Receive credentials:** `client_id` and `client_secret` upon approval
4. **Implement authentication** using the OAuth integration guide

**OAuth Flow:**
- Standard OAuth 2.0 authorization code flow
- Detailed integration instructions available in the OAuth documentation section

---

## API Reference

The PocketSmith API v2.0 is organized around the following resource categories:

### Users

**Endpoints:**
- Get authorised user
- Get user by ID
- Update user information

**Example - Get the Authorised User:**
```
GET https://api.pocketsmith.com/v2/me
```

**Purpose:** Gets the user that corresponds to the access token used in the request.

**Authentication Required:** Yes (Header-based credentials)

---

### Institutions

Manage financial institutions connected to user accounts.

**Operations:**
- Create institution
- Read institution details
- Update institution information
- Delete institution
- List all institutions within a user account

---

### Accounts

Complete account management functionality.

**Operations:**
- Get account details
- Update account information
- Delete account
- Create new account
- Manage account ordering within users
- List accounts by institution

---

### Transaction Accounts

Transaction accounts are the specific accounts where transactions are recorded.

**Operations:**
- Get transaction account details
- Update transaction account
- List transaction accounts by user

---

### Transactions

Complete transaction lifecycle management with multi-context querying.

**Query Contexts:**
- By user
- By account
- By category
- By transaction account

**Operations:**
- Create transactions within transaction accounts
- Read transaction details
- Update transactions
- Delete transactions
- Query and filter transactions

---

### Categories

Manage and organize transaction categories.

**Operations:**
- Category management and organization
- List user-specific categories
- Create category rules
- Update categories
- Delete categories

---

### Budgeting

Budget management and analysis features.

**Features:**
- Budget retrieval and summaries
- Trend analysis
- Forecast cache management

---

### Supporting Resources

Additional resources for comprehensive financial data management:

- **Events** - Manage financial events
- **Attachments** - Attach files to transactions
- **Labels** - Label and tag transactions
- **Saved Searches** - Save frequently used search queries
- **Currencies** - Handle multi-currency support
- **Time Zones** - Manage timezone settings

---

## Common Topics

### Pagination

The API uses pagination for endpoints that return multiple records.

**Implementation Details:**
- Refer to the pagination documentation section for page size limits and navigation
- Response headers typically include pagination metadata

### Error Handling

The API returns standard HTTP status codes.

**Common Status Codes:**
- `200 OK` - Successful request
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication failure
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

**Error Response Format:**
Detailed error handling documentation available at: https://developers.pocketsmith.com/docs

---

## Changelog

### v2.0 - Welcome to the new PocketSmith developer hub
**Posted:** Almost 7 years ago by Regan McEntyre

The development team announced an updated documentation portal: "We've given our developer documentation a bit of a spruce up. Come on in and check it out, and let us know what you think!"

**Current Status:**
- API Version 2.0 is the current stable version
- Interactive API documentation powered by OpenAPI 3 specification

---

## Support

**Contact the Development Team:**
- **Email:** [email protected]

**Resources:**
- **Interactive API Reference:** https://developers.pocketsmith.com/reference
- **Complete Guides:** https://developers.pocketsmith.com/docs
- **Changelog:** https://developers.pocketsmith.com/changelog

---

## Quick Start Guide

1. **For Personal Tools:**
   ```bash
   # Get your developer key from Settings > Security
   curl --header "X-Developer-Key: YOUR_KEY_HERE" \
     https://api.pocketsmith.com/v2/me
   ```

2. **For Multi-User Applications:**
   - Email [email protected] to register your app
   - Implement OAuth 2.0 flow once approved

3. **Explore the API:**
   - Start with the `/me` endpoint to verify authentication
   - Review the resource categories that match your use case
   - Test endpoints using the interactive reference

---

## Additional Notes

**OpenAPI Specification:**
The API documentation is built using OpenAPI 3, which means:
- Interactive testing tools available in the web interface
- Machine-readable API specifications
- Auto-generated client libraries possible

**Rate Limiting:**
Check the full documentation for any rate limiting policies.

**Best Practices:**
- Always handle errors gracefully
- Use pagination for large datasets
- Cache responses where appropriate
- Follow OAuth 2.0 best practices for multi-user apps

---

**End of Documentation**

For the most up-to-date information and interactive API testing, visit: https://developers.pocketsmith.com/
