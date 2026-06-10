================================================================================
SPECIFICATION: Security Testing Requirements
Category: Testing
Enforcement Level: CRITICAL (BLOCKING)
Version: 2.0
================================================================================

PURPOSE
-------
Define mandatory security tests that MUST pass before deployment.

SCOPE
-----
All Python web applications, especially those handling:
- User authentication
- Database operations
- User-generated content
- External API integrations

================================================================================
TEST FRAMEWORK REQUIREMENTS
================================================================================

Framework: pytest
Required Packages:
  - pytest (test runner)
  - pytest-cov (coverage reporting)
  - pytest-mock (mocking support)

Test File: tests/test_security.py (MANDATORY)

Coverage Requirement: 100% of security-critical code paths

================================================================================
MANDATORY TEST CATEGORIES
================================================================================

CATEGORY 1: Secrets Management Tests
CATEGORY 2: SQL Injection Prevention Tests
CATEGORY 3: XSS Prevention Tests
CATEGORY 4: CSRF Protection Tests
CATEGORY 5: Input Validation Tests
CATEGORY 6: Security Headers Tests
CATEGORY 7: Authentication/Authorization Tests
CATEGORY 8: Session Security Tests

================================================================================
CATEGORY 1: SECRETS MANAGEMENT TESTS
================================================================================

Purpose: Verify no hardcoded credentials exist

TEST-1.1: No Hardcoded Credentials in Source
  Method: Static analysis of source code
  Implementation: grep/regex patterns or detect-secrets tool
  Pass Criteria: Zero matches for:
    - password = "literal"
    - api_key = "sk-..."
    - secret = "hardcoded"
  Failure: Blocks deployment

TEST-1.2: Environment Variable Validation
  Method: Unit test with missing environment variables
  Steps:
    1. Unset required environment variable (e.g., DB_PASSWORD)
    2. Attempt to initialize application/DatabaseConnection
    3. Assert ValueError raised
    4. Verify error message is descriptive
  Pass Criteria: ValueError raised with clear message

TEST-1.3: Secrets Not in Logs
  Method: Capture logs during operations
  Steps:
    1. Set test secret in environment
    2. Run application operations
    3. Inspect log output
    4. Assert secret value NOT in logs
  Pass Criteria: No secret values logged

================================================================================
CATEGORY 2: SQL INJECTION PREVENTION TESTS
================================================================================

Purpose: Verify all database queries use parameterized statements

TEST-2.1: Parameterized Queries Verified
  Method: Mock database cursor, inspect execute() calls
  For each query function:
    1. Create mock cursor
    2. Call query function with test input
    3. Assert cursor.execute() called with:
       - Query string containing %s placeholders
       - Parameters as tuple (not string-formatted)

TEST-2.2: SQL Injection Attack Simulation
  Method: Attempt SQL injection via inputs
  Attack Inputs:
    - "' OR '1'='1"
    - "'; DROP TABLE users;--"
    - "1 UNION SELECT * FROM sensitive_table"
  Steps:
    1. Call query function with malicious input
    2. Verify query executes safely
    3. Verify input treated as literal (not executed)
  Pass Criteria: No data leaked, no tables dropped

TEST-2.3: No String Formatting in SQL
  Method: Static code analysis
  Scan for patterns:
    - f"SELECT
    - f"INSERT
    - cursor.execute.*f"
    - cursor.execute.*+
    - "SELECT.*%.*" %
  Pass Criteria: Zero matches

================================================================================
CATEGORY 3: XSS PREVENTION TESTS
================================================================================

Purpose: Verify output escaping prevents XSS attacks

TEST-3.1: Template Auto-Escaping Enabled
  Method: Check framework configuration
  Flask: assert app.jinja_env.autoescape == True
  Django: Check TEMPLATES['OPTIONS']['autoescape']
  Pass Criteria: Auto-escaping enabled

TEST-3.2: Malicious Script Tags Escaped
  Method: Render template with XSS payload
  Attack Input: "<script>alert('XSS')</script>"
  Steps:
    1. Insert payload into database/context
    2. Render template
    3. Inspect HTML output
    4. Assert contains: &lt;script&gt; (escaped)
    5. Assert NOT contains: <script> (raw)
  Pass Criteria: All HTML special chars escaped

TEST-3.3: No Unsafe Template Filters
  Method: Static analysis of template files
  Scan for:
    - {{ variable | safe }}
    - {{ variable | raw }}
    - {% autoescape off %}
  Pass Criteria: Zero matches (or documented exceptions only)

TEST-3.4: JavaScript Context Escaping
  Method: Test data in JavaScript contexts
  Attack Input: "'; alert('XSS'); //"
  Verify: Properly escaped in <script> tags

================================================================================
CATEGORY 4: CSRF PROTECTION TESTS
================================================================================

Purpose: Verify CSRF tokens required for state-changing operations

TEST-4.1: CSRF Protection Enabled
  Method: Check framework configuration
  Flask: Verify CSRFProtect initialized
  Django: Verify CsrfViewMiddleware in MIDDLEWARE
  Pass Criteria: CSRF protection configured

TEST-4.2: POST Without CSRF Token Rejected
  Method: Make POST request without token
  Steps:
    1. Create test client
    2. Make POST request to protected endpoint
    3. Do NOT include CSRF token
    4. Assert response status is 400 or 403
  Pass Criteria: Request rejected

TEST-4.3: POST With Valid CSRF Token Accepted
  Method: Make POST request with valid token
  Steps:
    1. Create test client
    2. Get CSRF token
    3. Make POST request with token
    4. Assert response status is 200
  Pass Criteria: Request accepted

TEST-4.4: Health Check Exempt from CSRF
  Method: Verify health endpoint works without CSRF
  Steps:
    1. Make GET request to /health (no token)
    2. Assert status is 200
  Pass Criteria: Health check accessible

================================================================================
CATEGORY 5: INPUT VALIDATION TESTS
================================================================================

Purpose: Verify user inputs are validated and sanitized

TEST-5.1: Whitelist Validation for Enums
  Method: Test with invalid enum values
  Example: status parameter
  Steps:
    1. Make request with invalid value (e.g., status=INVALID)
    2. Assert response is 400
    3. Assert error message descriptive
  Pass Criteria: Invalid values rejected

TEST-5.2: Numeric Input Validation
  Method: Test with non-numeric and out-of-range values
  Examples:
    - limit=abc → 400 error
    - limit=-10 → clamped to minimum or 400
    - limit=99999 → clamped to maximum or 400
  Pass Criteria: Invalid inputs rejected or clamped

TEST-5.3: Length Validation
  Method: Test with oversized inputs
  Steps:
    1. Send input exceeding maximum length
    2. Assert response is 400
    3. Assert error mentions length constraint
  Pass Criteria: Oversized inputs rejected

TEST-5.4: Required Field Validation
  Method: Test with missing required fields
  Steps:
    1. Send request missing required field
    2. Assert response is 400
    3. Assert error mentions missing field
  Pass Criteria: Missing required fields rejected

================================================================================
CATEGORY 6: SECURITY HEADERS TESTS
================================================================================

Purpose: Verify security headers present on all responses

TEST-6.1: Required Headers Present
  Method: Make request, inspect response headers
  Required Headers:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY or SAMEORIGIN
    - X-XSS-Protection: 1; mode=block
    - Content-Security-Policy: [defined policy]
  Pass Criteria: All headers present with correct values

TEST-6.2: HSTS Header in Production
  Method: Test with production configuration
  Steps:
    1. Set app.debug = False
    2. Make request
    3. Assert Strict-Transport-Security header present
    4. Assert header value includes max-age
  Pass Criteria: HSTS header present in non-debug mode

TEST-6.3: CSP Blocks Inline Scripts
  Method: Test CSP compliance
  Steps:
    1. Inspect CSP header
    2. Assert does NOT contain 'unsafe-inline' for script-src
    3. Or verify nonce/hash-based inline scripts
  Pass Criteria: CSP prevents unsafe inline scripts

================================================================================
CATEGORY 7: AUTHENTICATION/AUTHORIZATION TESTS
================================================================================

Purpose: Verify access controls enforced

TEST-7.1: Protected Routes Require Authentication
  Method: Access protected route without authentication
  Steps:
    1. Clear session/auth tokens
    2. Request protected resource
    3. Assert response is 401 or redirect to login
  Pass Criteria: Access denied

TEST-7.2: Authenticated Access Granted
  Method: Access protected route with valid auth
  Steps:
    1. Authenticate user
    2. Request protected resource
    3. Assert response is 200
  Pass Criteria: Access granted

TEST-7.3: Authorization Enforced (Resource Access)
  Method: Attempt to access another user's resource
  Steps:
    1. Authenticate as User A
    2. Request User B's resource
    3. Assert response is 403 Forbidden
  Pass Criteria: Access denied

TEST-7.4: Privilege Escalation Prevented
  Method: Attempt admin action as regular user
  Steps:
    1. Authenticate as non-admin
    2. Attempt admin operation
    3. Assert response is 403
  Pass Criteria: Admin actions require admin role

================================================================================
CATEGORY 8: SESSION SECURITY TESTS
================================================================================

Purpose: Verify session cookies configured securely

TEST-8.1: Session Cookies Have Secure Flags
  Method: Inspect Set-Cookie header
  Required Flags:
    - Secure (HTTPS only)
    - HttpOnly (no JavaScript access)
    - SameSite=Lax or Strict
  Pass Criteria: All flags present

TEST-8.2: Session Timeout Enforced
  Method: Test session expiration
  Steps:
    1. Create session
    2. Wait past timeout period
    3. Attempt authenticated action
    4. Assert session expired (401/redirect)
  Pass Criteria: Expired sessions rejected

TEST-8.3: Session Regeneration After Login
  Method: Verify session ID changes
  Steps:
    1. Get initial session ID
    2. Log in
    3. Get new session ID
    4. Assert IDs are different
  Pass Criteria: Session ID regenerated (prevents fixation)

================================================================================
TEST EXECUTION REQUIREMENTS
================================================================================

CI/CD Integration:
  - Run in security-scan stage (blocking)
  - Must pass before build stage
  - Generate coverage report

Command:
  pytest tests/test_security.py -v --cov=src --cov-report=term

Exit Code:
  - 0: All tests passed → proceed to next stage
  - Non-zero: Tests failed → BLOCK pipeline

Coverage:
  - Minimum: 100% of security-critical code
  - Report formats: terminal, XML, HTML

Reporting:
  - Failed tests logged with details
  - Coverage gaps identified
  - Security scan results archived

================================================================================
TESTING UTILITIES
================================================================================

Mock Database Cursor:
  Purpose: Verify parameterized queries without real DB

  Pattern:
    from unittest.mock import MagicMock

    mock_cursor = MagicMock()
    # Call function
    mock_cursor.execute.assert_called_with(
        "SELECT * FROM table WHERE id = %s",
        (value,)
    )

Test Client (Flask):
  Purpose: Make HTTP requests to app

  Pattern:
    @pytest.fixture
    def client():
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_example(client):
        response = client.get('/endpoint')
        assert response.status_code == 200

Environment Variable Mocking:
  Purpose: Test configuration validation

  Pattern:
    import os
    from unittest.mock import patch

    with patch.dict(os.environ, {}, clear=True):
        # Test with missing env vars
        pass

================================================================================
DOCUMENTATION REQUIREMENTS
================================================================================

Each Test Must Include:
  - Docstring explaining what is tested
  - Reference to applicable security spec
  - Clear pass/fail criteria
  - Attack vector being prevented

Example:
  def test_sql_injection_prevention():
      """
      Verify SQL injection attacks prevented via parameterized queries.

      Related Spec: specs/security/sql_injection_prevention.spec
      Attack Vector: Malicious SQL in user input
      Pass Criteria: Input treated as literal, not executed
      """

================================================================================
IMPLEMENTATION CHECKLIST
================================================================================

Before deployment:
[ ] tests/test_security.py exists
[ ] All 8 test categories implemented
[ ] 100% coverage of security-critical code
[ ] All tests passing locally
[ ] CI/CD pipeline runs security tests
[ ] Security test failures block deployment

During implementation:
[ ] Write tests alongside code (TDD)
[ ] Test both positive and negative cases
[ ] Test edge cases and attack vectors
[ ] Mock external dependencies appropriately
[ ] Document test purpose and pass criteria

================================================================================
END OF SPECIFICATION
================================================================================
