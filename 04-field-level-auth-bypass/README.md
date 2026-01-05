# Field-level Authorization Bypass

A document management system has been implemented with GraphQL. The developers added authorization checks to protect confidential documents, but they may have missed some access paths. Can you find a way to access the protected content?

## Difficulty

Medium

## How to Run

```bash
cd 04-field-level-auth-bypass
docker-compose -f docker-compose-dev.yml up --build
```

### Stopping the Challenge

```bash
docker-compose -f docker-compose-dev.yml down
```

## Accessing the Challenge

- **GraphQL Endpoint:** http://localhost:8004/graphql
- **GraphQL Playground:** http://localhost:8004/graphql
- **Health Check:** http://localhost:8004/health
