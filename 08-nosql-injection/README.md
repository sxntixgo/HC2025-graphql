# NoSQL Injection

A GraphQL API connects to a MongoDB database. One of the search endpoints accepts flexible filter parameters. Can you manipulate the query to access documents you shouldn't be able to see?

## Difficulty

Hard

## How to Run

```bash
cd 08-nosql-injection
docker-compose -f docker-compose-dev.yml up --build
```

### Stopping the Challenge

```bash
docker-compose -f docker-compose-dev.yml down
```

## Accessing the Challenge

- **GraphQL Endpoint:** http://localhost:8008/graphql
- **GraphQL Playground:** http://localhost:8008/graphql
- **Health Check:** http://localhost:8008/health
