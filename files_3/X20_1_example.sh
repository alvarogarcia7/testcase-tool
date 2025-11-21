#!/bin/bash
# Auto-generated test script
# Test Case: X20_1
# Requirement: X20

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "="*80
echo "Test Case: X20_1"
echo "Description: Verify that a user can successfully log in with valid credentials"
echo "="*80

# ============================================================================
# PREREQUISITES CHECK
# ============================================================================

check_prerequisites() {
    echo "${YELLOW}Checking prerequisites...${NC}"
    local failed=0

    echo "  [1] API server running on localhost:8080"
    # TODO: Add actual check for: API server running on localhost:8080
    echo "  [2] Test database populated with test user"
    # TODO: Add actual check for: Test database populated with test user

    if [ $failed -eq 0 ]; then
        echo "${GREEN}All prerequisites met${NC}"
        return 0
    else
        echo "${RED}Prerequisites check failed${NC}"
        return 1
    fi
}

check_prerequisites || exit 1

# ============================================================================
# TEST EXECUTION
# ============================================================================

# Step 1: Send login request with valid credentials
echo ""
echo "${YELLOW}Step 1: Send login request with valid credentials${NC}"
echo "-"*80

echo "Executing command 1..."
echo "Command: curl -X POST http://localhost:8080/api/login \..."

curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test@123"}'
STEP1_CMD1_STATUS=$?

echo "${GREEN}Step 1 completed${NC}"

# ============================================================================
# VERIFICATION / ASSERTIONS
# ============================================================================

echo ""
echo "${YELLOW}Running verification checks...${NC}"

# Expected outputs:
# - http_status should be: 200
# - response.success should be: True
# - response.token should: exists and not empty

echo "Verification 1: Verify response contains token"
echo $RESPONSE | jq -r '.token'
VERIFY1_STATUS=$?

# ============================================================================
# TEST SUMMARY
# ============================================================================

echo ""
echo "="*80
echo "${GREEN}Test execution completed${NC}"
echo "="*80
