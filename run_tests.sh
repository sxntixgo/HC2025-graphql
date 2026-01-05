#!/bin/bash

# GraphQL CTF Challenges Test Runner
# Run tests for all 8 challenges in The HACKERS CHALLENGE using Python test scripts

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results tracking
TOTAL_CHALLENGES=8
PASSED_CHALLENGES=0
FAILED_CHALLENGES=()

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  The HACKERS CHALLENGE - Test Runner  ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ python3 is required but not installed${NC}"
    exit 1
fi

# Function to run tests for a single challenge
run_challenge_test() {
    local challenge_num=$1
    local challenge_name=$2
    local test_script="test_${challenge_num}.py"
    
    echo -e "${YELLOW}Testing: $challenge_name${NC}"
    echo "----------------------------------------"
    
    cd "tests"
    
    # Check if Python test script exists
    if [[ ! -f "$test_script" ]]; then
        echo -e "${RED}❌ No Python test script ($test_script) found for $challenge_name${NC}"
        FAILED_CHALLENGES+=("$challenge_name (no test script)")
        cd ..
        return 1
    fi
    
    # Make test script executable
    chmod +x "$test_script"
    
    # Install test requirements if they exist
    if [[ -f "test-requirements.txt" ]]; then
        echo "📦 Installing test dependencies..."
        pip install -r test-requirements.txt --quiet || echo "⚠️ Warning: Could not install test dependencies"
    fi
    
    # Run the Python test
    if python3 "$test_script"; then
        echo -e "${GREEN}✅ $challenge_name: PASSED${NC}"
        ((PASSED_CHALLENGES++))
    else
        echo -e "${RED}❌ $challenge_name: FAILED${NC}"
        FAILED_CHALLENGES+=("$challenge_name")
    fi
    
    cd ..
    echo ""
}

# Test each challenge
echo -e "${BLUE}Running tests for all challenges...${NC}"
echo ""

# Create and activate virtual environment for tests
echo "🔧 Setting up Python virtual environment..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo "✅ Virtual environment activated"

run_challenge_test "01_naive_introspection" "Naive Introspection"
run_challenge_test "02_schema_introspection" "Schema Introspection"
run_challenge_test "03_error_message_leakage" "Error Message Leakage"  
run_challenge_test "04_field_level_auth_bypass" "Field-level Authorization Bypass"
run_challenge_test "05_nested_query_bypass" "Nested Query Bypass"
run_challenge_test "06_batch_query_auth_bypass" "Batch Query Authorization Bypass"
run_challenge_test "07_graphql_injection" "GraphQL Injection"
run_challenge_test "08_nosql_injection" "NoSQL Injection"

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}               SUMMARY                  ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [[ $PASSED_CHALLENGES -eq $TOTAL_CHALLENGES ]]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! ($PASSED_CHALLENGES/$TOTAL_CHALLENGES)${NC}"
    echo -e "${GREEN}All GraphQL CTF challenges are working correctly!${NC}"
    deactivate 2>/dev/null || true
    exit 0
else
    echo -e "${RED}❌ Some tests failed ($PASSED_CHALLENGES/$TOTAL_CHALLENGES passed)${NC}"
    echo ""
    echo -e "${RED}Failed challenges:${NC}"
    for challenge in "${FAILED_CHALLENGES[@]}"; do
        echo -e "${RED}  - $challenge${NC}"
    done
    echo ""
    echo -e "${YELLOW}Please check the individual challenge logs above for details.${NC}"
    deactivate 2>/dev/null || true
    exit 1
fi

# Deactivate virtual environment
deactivate 2>/dev/null || true