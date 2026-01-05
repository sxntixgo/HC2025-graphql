# Claude Code Configuration

## GraphQL Security Challenges

This project contains 8 GraphQL security challenges, each in its own numbered folder. Each challenge demonstrates a specific GraphQL vulnerability and contains the minimum code required to solve that particular security issue.

### Challenge Overview

1. **01-naive-introspection** - Naive Introspection vulnerability (flag exposed in field names)
2. **02-schema-introspection** - Schema Introspection vulnerability (flag in hidden fields)
3. **03-error-message-leakage** - Error Message Information Leakage vulnerability
4. **04-field-level-auth-bypass** - Field-level Authorization Bypass vulnerability
5. **05-nested-query-bypass** - Nested Query Authorization Bypass vulnerability
6. **06-batch-query-auth-bypass** - Batch Query Authorization Bypass vulnerability
7. **07-graphql-injection** - GraphQL/SQL Injection vulnerability
8. **08-nosql-injection** - NoSQL Injection vulnerability

### Challenge Structure

Each challenge folder contains:
- `app.py` or `server.js` - Flask/Node.js application implementing the specific GraphQL vulnerability (must contain only minimum code required for the challenge)
- `.env` - Environment file containing the challenge flag
- `docker-compose-dev.yml` - Development Docker configuration
- `README.md` - Challenge description and solution walkthrough
- Other supporting files (requirements.txt, package.json, etc.)

### Testing Structure

All test files are centralized in the `tests/` directory:
- `tests/test_01_naive_introspection.py` - Naive introspection challenge tests
- `tests/test_02_schema_introspection.py` - Schema introspection challenge tests
- `tests/test_03_error_message_leakage.py` - Error message leakage challenge tests
- `tests/test_04_field_level_auth_bypass.py` - Field-level auth bypass challenge tests
- `tests/test_05_nested_query_bypass.py` - Nested query bypass challenge tests
- `tests/test_06_batch_query_auth_bypass.py` - Batch query auth bypass challenge tests
- `tests/test_07_graphql_injection.py` - GraphQL injection challenge tests
- `tests/test_08_nosql_injection.py` - NoSQL injection challenge tests
- `tests/test-requirements.txt` - Python test dependencies
- `tests/TEST_README.md` - Detailed testing documentation

## Testing Requirements

This project uses centralized Python-based testing for all GraphQL security challenges. All test scripts are located in the `tests/` folder and orchestrated by the top-level `run_tests.sh` script.

### Running Tests

#### Run All Tests
To run tests for all challenges at once:
```bash
./run_tests.sh
```

#### Run Individual Challenge Tests
To run tests for a specific challenge:
```bash
cd tests/
python3 test_01_schema_introspection.py
```

### Test Structure

The centralized tests directory contains:
- Individual Python test scripts for each challenge
- Shared test requirements and documentation  
- All test scripts automatically handle Docker service lifecycle

### Test Script Requirements

All test scripts follow these conventions:
- Use Python 3 with the `requests` library for HTTP/GraphQL testing
- Automatically start and stop Docker Compose services
- Wait for services to be ready before running tests
- Report test results with colored output
- Exit with appropriate status codes (0 for success, 1 for failure)

### Port Configuration

Each challenge uses a sequential port mapping:
- 01-naive-introspection: `http://localhost:8001`
- 02-schema-introspection: `http://localhost:8002`
- 03-error-message-leakage: `http://localhost:8003`
- 04-field-level-auth-bypass: `http://localhost:8004`
- 05-nested-query-bypass: `http://localhost:8005`
- 06-batch-query-auth-bypass: `http://localhost:8006`
- 07-graphql-injection: `http://localhost:8007`
- 08-nosql-injection: `http://localhost:8008`

### Important Development Guidelines

- **Application Requirements**: Each `app.py` or `server.js` must contain only the minimum code required to demonstrate the specific GraphQL vulnerability. Do not add unnecessary features, middleware, or functionality beyond what's needed for the challenge.
- **Health Endpoint Requirement**: All applications MUST include a `/health` endpoint that returns `{'status': 'healthy'}`. This endpoint is required for Docker health checks and should never be deleted. Example implementations:

  **Python/Flask:**
  ```python
  @app.route('/health')
  def health():
      return jsonify({'status': 'healthy'})
  ```

  **Node.js/Express:**
  ```javascript
  app.get('/health', (req, res) => {
    res.json({ status: 'healthy' });
  });
  ```

- **Flag Storage**: Each challenge's flag is stored in the `.env` file and should be accessible through exploiting the specific vulnerability.
- **Challenge Focus**: Each challenge should demonstrate exactly one vulnerability type and remain focused on that security issue.
- **Solution Documentation**: `README.md` files must NOT contain actual flag values. They should describe how to obtain the flag but not reveal the flag itself. This prevents spoilers and maintains the challenge integrity.
- **Read-Only Database (07-graphql-injection)**: Challenge 07 uses a read-only SQLite database to prevent destructive operations. The database is created during Docker build with `init-db.js` and mounted as read-only. This prevents players from dropping tables or modifying data while preserving the SQL injection vulnerability for learning.

### Test Commands for Claude Code

When working with this project, use these commands:

#### To run all tests:
```bash
./run_tests.sh
```

#### To run a specific challenge test:
```bash
cd tests/
python3 test_<challenge_number>_<challenge_name>.py
```


#### To lint and typecheck (if available):
Check individual challenge directories for specific linting requirements.

### Dependencies

The test scripts require:
- Python 3.x
- `requests` library
- Docker and docker-compose
- curl (for health checks)

Test dependencies are automatically installed from `test-requirements.txt` files where present.