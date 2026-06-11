# Enterprise Python Application - AI Development Standards

## Context
This is an **enterprise-grade Python web application** scaffolded from the approved template.
All code MUST comply with enterprise security, architecture, and deployment standards.

---

## CRITICAL: Standards Compliance is MANDATORY

This project is generated from an **enterprise golden path template** with built-in guardrails.
The specifications in `specs/` directory are **BINDING REQUIREMENTS**, not suggestions.

**Before writing ANY code:**
1. Read `docs/ENTERPRISE_STANDARDS.md` for compliance requirements
2. Review relevant specification files in `specs/` directory
3. Follow security patterns defined in `specs/security/`
4. Implement architecture patterns from `specs/architecture/`
5. Ensure deployment compliance per `specs/deployment/`

---

## Non-Negotiable Security Requirements

### 1. ZERO HARDCODED SECRETS
**ABSOLUTE RULE: No credentials, API keys, passwords, or secrets in source code. EVER.**

✅ **ONLY APPROVED METHOD:**
```python
import os
credential = os.environ.get('CREDENTIAL_NAME')
if not credential:
    raise ValueError("Required credential CREDENTIAL_NAME not set")
```

❌ **FORBIDDEN - Will fail security scan:**
```python
password = "any_literal_string"
api_key = "hardcoded-value"
DB_PASSWORD = "thoughts123"
```

**Enforcement:** Code will be scanned for hardcoded secrets. Any violations block deployment.

---

### 2. SQL INJECTION PREVENTION
**ABSOLUTE RULE: 100% of database queries MUST use parameterized statements.**

✅ **ONLY APPROVED METHOD:**
```python
cursor.execute("SELECT * FROM table WHERE column = %s", (user_input,))
cursor.execute("SELECT * FROM table WHERE col1 = %s AND col2 = %s", (val1, val2))
```

❌ **FORBIDDEN - Critical security vulnerability:**
```python
cursor.execute(f"SELECT * FROM table WHERE column = '{user_input}'")
cursor.execute("SELECT * FROM table WHERE id = " + str(value))
cursor.execute("SELECT * FROM table WHERE name = '%s'" % name)
```

**Enforcement:** Security tests will fail if any non-parameterized queries exist.

---

### 3. DEPENDENCY SECURITY
**ABSOLUTE RULE: All dependencies MUST be pinned, vetted, and free of known CVEs.**

✅ **ONLY APPROVED METHOD:**
```
# requirements.txt
Flask==3.0.3  # Pinned with ==
psycopg2-binary==2.9.9
```

❌ **FORBIDDEN:**
```
Flask>=2.0  # Loose version constraint
requests  # Unpinned version
some-deprecated-package==1.0.0  # Known CVEs
```

**Enforcement:** CI/CD pipeline runs `pip-audit`. Any CVEs block deployment.

---

### 4. CONTAINER SECURITY
**ABSOLUTE RULE: Containers MUST use Red Hat UBI images and run as non-root.**

✅ **ONLY APPROVED BASE IMAGES (Red Hat UBI):**
- `registry.access.redhat.com/ubi9/python-311:latest`
- `registry.access.redhat.com/ubi9/python-39:latest`
- `registry.access.redhat.com/ubi8/python-39:latest`

**Why Red Hat UBI:**
- Enterprise-grade security patches from Red Hat
- Already runs as non-root user (UID 1001)
- Free to use and redistribute
- Optimized for OpenShift/Kubernetes
- Compliance and certification ready

❌ **FORBIDDEN BASE IMAGES:**
- `python:latest` (unpredictable)
- `python:3.8` or older (EOL, no security patches)
- `python:alpine` (compatibility issues)
- Generic Python/Ubuntu/Debian images (use Red Hat UBI)
- Non-Red Hat images in enterprise environments

**Enforcement:** Container scanning blocks images with HIGH/CRITICAL CVEs.

---

### 5. WEB APPLICATION SECURITY
**ABSOLUTE RULE: All web apps MUST implement OWASP Top 10 protections.**

Required for ALL Flask/Django/FastAPI applications:
- ✅ CSRF protection enabled
- ✅ Security headers (CSP, X-Frame-Options, etc.)
- ✅ Input validation with whitelisting
- ✅ Output encoding/escaping (XSS prevention)
- ✅ Secure session management
- ✅ HTTPS enforcement in production

**Enforcement:** Security tests verify these controls are present.

---

## How to Use This Template

### Phase 1: Planning (REQUIRED)
Before writing code, understand the requirements:
1. Read `docs/ENTERPRISE_STANDARDS.md`
2. Review architecture patterns in `specs/architecture/`
3. Identify which security controls apply to your use case

### Phase 2: Implementation (FOLLOW SPECS)
Implement following the specifications:
1. Database layer: Follow `specs/architecture/database_layer.spec`
2. Web application: Follow `specs/architecture/web_application.spec`
3. Security: Implement patterns from `specs/security/`
4. Testing: Follow `specs/testing/security_tests.spec`

### Phase 3: Validation (GATE-CHECKED)
Before marking complete:
1. Run security tests: `pytest tests/test_security.py -v`
2. Run SBOM scan: `cyclonedx-py requirements -o sbom.json`
3. Run vulnerability scan: `pip-audit`
4. Run container scan: `trivy image <image-name>`
5. Verify all specs compliance

**ALL validation steps MUST pass before deployment.**

---

## Specification Files Reference

| Spec File | Purpose | When to Use |
|-----------|---------|-------------|
| `specs/security/secrets_management.spec` | How to handle credentials | Always - every project |
| `specs/security/sql_injection_prevention.spec` | Database query security | When using SQL databases |
| `specs/security/web_security.spec` | Web app security controls | Flask/Django/FastAPI apps |
| `specs/architecture/database_layer.spec` | DB connection patterns | When connecting to databases |
| `specs/architecture/web_application.spec` | Web app structure | Web applications |
| `specs/testing/security_tests.spec` | Required security tests | Always - every project |
| `specs/deployment/dockerfile.spec` | Container requirements | When building containers |
| `specs/deployment/ci_cd_pipeline.spec` | Pipeline requirements | Always - every project |

---

## AI Code Generation Guidelines

### When generating code for this project:

**DO:**
1. **Start with specs** - Always read the relevant .spec file first
2. **Validate inputs** - Whitelist allowed values, reject invalid input
3. **Escape outputs** - Prevent XSS in all rendered content
4. **Use type hints** - All functions should have type annotations
5. **Log security events** - Failed auth, invalid input, etc.
6. **Handle errors gracefully** - Don't leak sensitive info in error messages
7. **Write tests** - Include security tests for all security-critical code

**DON'T:**
1. **Hardcode secrets** - Not even for "testing" or "temporary" purposes
2. **String concatenate SQL** - EVER. Use parameterized queries.
3. **Trust user input** - Validate everything from users/external systems
4. **Bypass security controls** - Don't disable CSRF, skip validation, etc.
5. **Use deprecated packages** - Check approval list in specs
6. **Run as root** - Containers must use non-root user
7. **Assume data is safe** - Escape/encode all output

---

## Common Scenarios & Required Actions

### Scenario: Need to connect to a database
→ **Action:** Implement per `specs/architecture/database_layer.spec`
→ **Security:** Use `specs/security/secrets_management.spec` for credentials
→ **Testing:** Add tests per `specs/testing/security_tests.spec` (SQL injection section)

### Scenario: Need to accept user input
→ **Action:** Validate per `specs/security/web_security.spec` (Input Validation section)
→ **Security:** Whitelist allowed values, reject malformed input
→ **Testing:** Add input validation tests

### Scenario: Need to display user-generated content
→ **Action:** Implement output encoding per `specs/security/web_security.spec` (XSS Prevention)
→ **Security:** Use auto-escaping (Jinja2 double braces, Django template double braces)
→ **Testing:** Add XSS prevention tests

### Scenario: Need to add a new dependency
→ **Action:** Check against approved packages list
→ **Security:** Run `pip-audit` to verify no known CVEs
→ **Requirements:** Pin to specific version with ==

---

## Approval Gates

Code cannot be deployed until it passes ALL gates:

- [ ] **Security Scan**: No secrets detected
- [ ] **Dependency Scan**: No CVEs in dependencies
- [ ] **SBOM Generation**: Software bill of materials created
- [ ] **Container Scan**: No HIGH/CRITICAL vulnerabilities
- [ ] **Security Tests**: All security tests passing
- [ ] **Spec Compliance**: Follows all applicable .spec files
- [ ] **Code Review**: Approved by senior engineer (human)

---

## What to Ask Before Implementing

If you encounter these, **STOP and ASK the user:**

1. **New database queries** - Should they be read-only? Need connection pooling?
2. **User authentication** - SSO required? OAuth provider?
3. **External API calls** - Rate limiting? Timeout configuration?
4. **File uploads** - Size limits? Allowed file types? Virus scanning?
5. **Sensitive data** - PII? Need encryption at rest?
6. **Authorization** - Role-based? Attribute-based?

**Don't make assumptions. Confirm requirements.**

---

## Support & Escalation

- **Security questions**: Review `docs/ENTERPRISE_STANDARDS.md`
- **Spec clarification**: Check specification file in `specs/`
- **Compliance issues**: Escalate to security team
- **Architecture decisions**: Escalate to platform engineering

---

## Success Criteria

Implementation is complete when:
- ✅ All applicable specifications implemented
- ✅ Security tests pass (100% coverage on security controls)
- ✅ No hardcoded secrets exist
- ✅ All database queries use parameterized statements
- ✅ Container runs as non-root user
- ✅ Security headers configured
- ✅ Input validation implemented
- ✅ Output encoding implemented
- ✅ Dependencies pinned and scanned
- ✅ SBOM generated and clean
- ✅ Container scan passes (no HIGH/CRITICAL)
- ✅ CI/CD pipeline configured per specs

**When in doubt, refer to the specifications. They are the source of truth.**
