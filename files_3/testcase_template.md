# Test Case: X20_1

**Requirement ID:** X20

**Tags:** integration, api, smoke
**Categories:** authentication, backend

## Description

Detailed description of what this test case validates.
Can be multi-line and include the purpose, scope, and any
important context about the test.

## Prerequisites

- Database is running and accessible
- Test user account exists with credentials (user: testuser, pass: test123)
- API server is running on port 8080
- Required test data is seeded in the database

## Test Steps

### Step 1: Initialize test environment

*Note: Optional notes about this step*

**Commands:**
```bash
docker-compose up -d
sleep 5
```

### Step 2: Run authentication test

**Commands:**
```bash
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"user":"testuser","password":"test123"}'
```

### Step 3: Verify token

**Commands:**
```bash
python scripts/verify_token.py --token $AUTH_TOKEN
echo "Token verification complete"
```

## Expected Result

User should be successfully authenticated and receive a valid JWT token.
The token should be valid for 24 hours and contain the correct user claims.

**Expected Outputs:**
- `status_code`: 200
- `response.token`: is not null
- `response.expires_in`: 86400

**Verification Commands:**
```bash
# Verify token is valid
jwt decode $AUTH_TOKEN
# Check token expiration
python scripts/check_token_expiry.py --token $AUTH_TOKEN
```

## Actual Execution Results

**Execution Info:**
- **Date:** 2025-01-15T10:30:00Z
- **Executed by:** qa-automation
- **Environment:** staging
- **Log File:** `X20_1.actual.log`

**Summary:**
- **Total Steps:** 3
- **Total Commands:** 5
- **Total Duration Ms:** 8446
- **Overall Status:** SUCCESS

### Execution Log

#### Step 1: Send login request with valid credentials

*Timestamp: 2025-01-15T14:23:45Z*

**Command 1:**
```bash
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test@123"}'

```

**Status Code:** 0 ✅
**Duration:** 156ms

**Output:**
```
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6InRlc3R1c2VyIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
  "user_id": 123,
  "username": "testuser",
  "expires_in": 86400
}
```

### Environment Details

- **Hostname:** test-runner-01
- **Os:** Linux 5.15.0-91-generic
- **Python Version:** 3.11.4
- **Shell:** /bin/bash
- **Working Directory:** /home/qa/tests

## Verification Results

**Overall Status:** PASS ✅

**Verification Steps:**

| Check | Result |
|-------|--------|
| Status code is 200 | PASS ✅ |
| Token is present in response | PASS ✅ |
| Token expiry is 24 hours | PASS ✅ |
| Token contains correct user claims | PASS ✅ |

**Comments:**

Test executed successfully. All verification steps passed.
Token was validated and contains expected claims.

**Execution Details:**
- **Date:** 2025-01-15T10:30:00Z
- **Executed by:** john.doe@example.com
- **Environment:** staging

**Notes:**

Any additional observations or notes about the test execution.
