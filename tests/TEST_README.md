# Schema Introspection Challenge - Testing Guide

This directory contains comprehensive tests for the Schema Introspection Challenge.

## Quick Start

### 1. Run Automated Tests
```bash
./run_tests.sh
```

This script will:
- Start the challenge using docker-compose
- Wait for services to be ready
- Run comprehensive automated tests
- Clean up afterward

### 2. Manual Testing
```bash
# Start the challenge
docker-compose -f docker-compose-dev.yml up -d

# Run manual tests (interactive)
./manual_test.sh

# Stop the challenge
docker-compose -f docker-compose-dev.yml down
```

### 3. Individual Test Commands

**Check service health:**
```bash
curl http://localhost:8001/health
```

**Basic GraphQL query:**
```bash
curl -X POST http://localhost:8001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "query { users { id username email } }"}'
```

**Schema introspection (discover hidden fields):**
```bash
curl -X POST http://localhost:8001/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query IntrospectionQuery { __schema { queryType { fields { name type { name ofType { name } } } } } }"
  }'
```

**Get the flag:**
```bash
curl -X POST http://localhost:8001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "query { adminNotes { id title content flag } }"}'
```

## Test Files

- `test_challenge.py` - Comprehensive automated test suite
- `run_tests.sh` - Full test runner with environment setup
- `manual_test.sh` - Interactive manual testing script
- `test-requirements.txt` - Python dependencies for testing

## Test Coverage

The automated tests cover:

1. **Service Health** - Verify the service starts and responds
2. **Basic GraphQL Access** - Test standard queries work
3. **Schema Introspection** - Verify introspection is enabled
4. **Hidden Field Discovery** - Test discovery of `adminNotes` field
5. **Type Exploration** - Test `SecretNote` type structure discovery
6. **Flag Retrieval** - Test accessing the hidden flag
7. **GraphiQL Interface** - Verify the GraphiQL interface is available
8. **Solution Commands** - Test all curl commands from SOLUTION.md

## Expected Results

When the challenge is working correctly:

1. **Service starts** without the nginx "host not found" error
2. **All tests pass** (10/10)
3. **Flag is retrievable** through schema introspection vulnerability
4. **Hidden `adminNotes` field** is discoverable via introspection

## Troubleshooting

### Common Issues

**Nginx "host not found" error:**
- Fixed by adding health checks and proper service dependencies
- Nginx now waits for the Flask app to be fully ready

**Service not ready:**
- The test scripts wait up to 120 seconds for services to start
- Check `docker-compose logs` if startup fails

**Tests fail:**
- Ensure port 8080 is not in use by other services
- Check that Docker and docker-compose are properly installed
- Verify curl and python3 are available

### Debugging

**View service logs:**
```bash
docker-compose -f docker-compose-dev.yml logs
```

**Check container status:**
```bash
docker-compose -f docker-compose-dev.yml ps
```

**Run specific test:**
```bash
python3 test_challenge.py --test test_access_hidden_admin_notes_without_auth
```

## Challenge Architecture

The fixed challenge now includes:

1. **Flask App** with health check endpoint
2. **Nginx** with proper upstream configuration and timeouts  
3. **Health Checks** - App reports health status
4. **Service Dependencies** - Nginx waits for app to be healthy
5. **Hidden Field** - `adminNotes` discoverable via introspection
6. **Flag Field** - Accessible through the hidden field

This demonstrates a realistic scenario where developers accidentally expose sensitive fields through GraphQL introspection.