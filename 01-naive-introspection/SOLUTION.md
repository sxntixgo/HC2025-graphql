# Solution: Naive Introspection

## Overview

This challenge demonstrates a naive GraphQL introspection vulnerability where sensitive information (the flag) is accidentally exposed in field names within the GraphQL schema.

## Step 1: Reconnaissance

Access the GraphQL endpoint and explore what queries are available using introspection:

```bash
curl -X POST http://localhost:8001/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { __schema { queryType { name } } }"
  }'
```

This confirms the GraphQL endpoint is accessible and introspection is enabled.

## Step 2: Vulnerability Identification

Perform a detailed introspection query to discover all available fields in the Query type:

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
curl -X POST http://localhost:8001/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { __schema { queryType { fields { name type { name ofType { name } } } } } }"
  }'
```

Examining the response reveals standard fields like `users` and `publicData`, but also an unusual field name that contains encoded flag content.

## Step 3: Exploitation

The flag is embedded directly in one of the field names. Look for field names that follow an unusual pattern - the flag format uses underscores to replace special characters like braces and hyphens.

The field name itself IS the flag, just with character substitutions:
- `___` represents `{`
- `__` represents `}` or `-`

## Step 4: Flag Retrieval

Decode the field name by reversing the substitutions:
1. Find the field name starting with `HC`
2. Replace `___` with `{`
3. Replace the final `__` with `}`
4. Replace intermediate `__` with `-`

The flag follows the format: `HC{...}`
