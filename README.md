# The HACKERS CHALLENGE - GraphQL Security Vulnerabilities

A collection of 8 GraphQL security challenges demonstrating common vulnerabilities and attack vectors. Each challenge is a self-contained Docker application showcasing a specific GraphQL security flaw.

## 🎯 Challenges Overview

| Challenge | Vulnerability | Difficulty | Port |
|-----------|---------------|------------|------|
| [01-naive-introspection](./01-naive-introspection/) | Naive Introspection (Flag in Field Names) | Easy | 8001 |
| [02-schema-introspection](./02-schema-introspection/) | Schema Introspection (Hidden Admin Fields) | Easy | 8002 |
| [03-error-message-leakage](./03-error-message-leakage/) | Error Message Information Leakage | Medium | 8003 |
| [04-field-level-auth-bypass](./04-field-level-auth-bypass/) | Field-level Authorization Bypass | Medium | 8004 |
| [05-nested-query-bypass](./05-nested-query-bypass/) | Nested Query Authorization Bypass | Medium | 8005 |
| [06-batch-query-auth-bypass](./06-batch-query-auth-bypass/) | Batch Query Authorization Bypass | Medium | 8006 |
| [07-graphql-injection](./07-graphql-injection/) | GraphQL/SQL Injection | Hard | 8007 |
| [08-nosql-injection](./08-nosql-injection/) | NoSQL Injection | Hard | 8008 |

## 🚀 Quick Start

### Run Individual Challenge
```bash
cd 01-naive-introspection
docker-compose -f docker-compose-dev.yml up -d
# Access GraphiQL at http://localhost:8001/graphql
```

## 🔍 Vulnerability Types Covered

### 1. **Introspection Vulnerabilities**
- Naive exposure of flags in field names
- Discovery of hidden admin fields through schema introspection

### 2. **Information Disclosure**
- Sensitive data leakage through error messages
- Verbose error responses revealing internal system details

### 3. **Authorization Issues**
- Field-level authorization bypass
- Rate limiting bypass through batch queries
- Privilege escalation vulnerabilities

### 4. **Injection Attacks**
- SQL injection through GraphQL parameters
- NoSQL injection via MongoDB query objects
- Cross-query data access

## 📁 Project Structure

```
graphql/
├── 01-naive-introspection/          # Challenge 1
├── 02-schema-introspection/         # Challenge 2
├── 03-error-message-leakage/        # Challenge 3
├── 04-field-level-auth-bypass/      # Challenge 4
├── 05-nested-query-bypass/          # Challenge 5
├── 06-batch-query-auth-bypass/      # Challenge 6
├── 07-graphql-injection/            # Challenge 7
├── 08-nosql-injection/              # Challenge 8
├── tests/                           # Test suite
├── CLAUDE.md                        # Development guidelines
├── run_tests.sh                     # Test runner script
└── README.md                        # This file
```

## 🚦 Development & Testing

### Health Endpoints
All applications include `/health` endpoints for monitoring:
```bash
curl http://localhost:8001/health
# Returns: {"status": "healthy"}
```

### Environment Setup
The test suite uses a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r tests/test-requirements.txt
```

### Docker Management
Each challenge can be managed independently:
```bash
# Start a challenge
docker-compose -f docker-compose-dev.yml up -d

# Stop a challenge  
docker-compose -f docker-compose-dev.yml down

# View logs
docker-compose -f docker-compose-dev.yml logs
```

## 🧪 Testing Framework

The project includes a comprehensive test suite that:
- Automatically starts/stops Docker services
- Tests vulnerability exploitation
- Validates security controls
- Provides detailed reporting

### Run All Tests
```bash
./run_tests.sh
```

### Run Individual Test
```bash
cd tests/
python3 test_01_naive_introspection.py
```