# Nested Query Authorization Bypass

A GraphQL API protects its admin endpoints from direct access. However, the same data might be accessible through other query paths. Can you find an alternative route to the protected data?

## Difficulty

Medium

## How to Run

```bash
cd 05-nested-query-bypass
docker-compose -f docker-compose-dev.yml up --build
```

### Stopping the Challenge

```bash
docker-compose -f docker-compose-dev.yml down
```

## Accessing the Challenge

- **GraphQL Endpoint:** http://localhost:8005/graphql
- **GraphQL Playground:** http://localhost:8005/graphql
- **Health Check:** http://localhost:8005/health
