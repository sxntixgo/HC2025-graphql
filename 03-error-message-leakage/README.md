# Error Message Leakage

A GraphQL API with user and file management capabilities has verbose error handling enabled. The developers forgot to sanitize error messages before sending them to clients. Can you trigger an error that reveals sensitive information?

## Difficulty

Medium

## How to Run

```bash
cd 03-error-message-leakage
docker-compose -f docker-compose-dev.yml up --build
```

### Stopping the Challenge

```bash
docker-compose -f docker-compose-dev.yml down
```

## Accessing the Challenge

- **GraphQL Endpoint:** http://localhost:8003/graphql
- **GraphQL Playground:** http://localhost:8003/graphql
- **Health Check:** http://localhost:8003/health
