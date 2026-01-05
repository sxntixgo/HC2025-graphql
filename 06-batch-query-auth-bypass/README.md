# Batch Query Authorization Bypass

A GraphQL API implements rate limiting to protect sensitive endpoints. Individual requests to protected endpoints are blocked, but the rate limiting logic might have a flaw. Can you find a way to bypass the protection?

## Difficulty

Medium

## How to Run

```bash
cd 06-batch-query-auth-bypass
docker-compose -f docker-compose-dev.yml up --build
```

### Stopping the Challenge

```bash
docker-compose -f docker-compose-dev.yml down
```

## Accessing the Challenge

- **GraphQL Endpoint:** http://localhost:8006/graphql
- **GraphQL Playground:** http://localhost:8006/graphql
- **Health Check:** http://localhost:8006/health
