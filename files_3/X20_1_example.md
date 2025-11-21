# Test Case: X20_1

**Requirement ID:** X20

**Tags:** authentication, critical
**Categories:** security, user-management

## Description

Verify that a user can successfully log in with valid credentials
and receive a valid authentication token.

## Prerequisites

- API server running on localhost:8080
- Test database populated with test user

## Test Steps

### Step 1: Send login request with valid credentials

**Commands:**
```bash
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test@123"}'
```

## Expected Result

API should return HTTP 200 with authentication token and user details.

**Expected Outputs:**
- `http_status`: 200
- `response.success`: True
- `response.token`: exists and not empty

**Verification Commands:**
```bash
# Verify response contains token
echo $RESPONSE | jq -r '.token'
```

## Actual Execution Results

**Execution Info:**
- **Date:** 2025-01-15T14:23:45Z
- **Executed by:** qa-automation
- **Environment:** staging
- **Log File:** `X20_1.actual.log`

**Summary:**
- **Total Steps:** 1
- **Total Commands:** 1
- **Total Duration Ms:** 156
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
| HTTP status is 200 | PASS ✅ |
| Response contains success:true | PASS ✅ |
| Token is present and non-empty | PASS ✅ |

**Comments:**

Test passed successfully. User authenticated and received valid token.

**Execution Details:**
- **Date:** 2025-01-15T14:23:45Z
- **Executed by:** qa-automation
- **Environment:** staging
