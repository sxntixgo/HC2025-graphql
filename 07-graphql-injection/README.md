# GraphQL SQL Injection

A GraphQL API connects to a SQLite database to manage users and documents. The search functionality might not be properly sanitizing inputs. Can you exploit a vulnerability to access confidential data?

## Difficulty

Hard

## How to Run

```bash
cd 07-graphql-injection
docker-compose -f docker-compose-dev.yml up --build
```

### Stopping the Challenge

```bash
docker-compose -f docker-compose-dev.yml down
```

## Accessing the Challenge

- **GraphQL Endpoint:** http://localhost:8007/graphql
- **GraphQL Playground:** http://localhost:8007/graphql
