# Schema Introspection

You've discovered a GraphQL API for a notes application. The public documentation only mentions a few basic queries, but there might be more hidden in the schema. Can you discover what the developers tried to hide?

## Difficulty

Easy

## How to Run

```bash
cd 02-schema-introspection
docker-compose -f docker-compose-dev.yml up --build
```

### Stopping the Challenge

```bash
docker-compose -f docker-compose-dev.yml down
```

## Accessing the Challenge

- **GraphQL Endpoint:** http://localhost:8002/graphql
- **GraphQL Playground:** http://localhost:8002/graphql
- **Health Check:** http://localhost:8002/health
