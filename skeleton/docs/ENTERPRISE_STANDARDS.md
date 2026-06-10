# Enterprise Python Application Standards

**Version:** 2.0  
**Last Updated:** 2026-06-10  
**Enforcement:** MANDATORY for all production deployments

---

## Purpose

This document defines **binding standards** for Python application development within the enterprise.
All applications MUST comply with these standards to pass security review and deploy to production.

These standards exist to:
1. Prevent security vulnerabilities (OWASP Top 10)
2. Ensure supply chain security (SBOM, dependency scanning)
3. Enforce container security best practices
4. Maintain compliance with regulatory requirements
5. Enable consistent code review and auditing

---

## Compliance Levels

### LEVEL 1: CRITICAL (BLOCKING)
Violations **PREVENT deployment**. No exceptions without CISO approval.
- Hardcoded secrets/credentials
- SQL injection vulnerabilities
- Known CVEs in dependencies (HIGH/CRITICAL)
- Running containers as root
- Missing security headers (CSP, X-Frame-Options)

### LEVEL 2: REQUIRED (ENFORCED)
Violations **BLOCK merge** to main branch.
- Missing SBOM generation
- Unpinned dependencies
- Missing security tests
- No input validation
- Deprecated Python versions (< 3.11)

### LEVEL 3: RECOMMENDED (MONITORED)
Violations logged but don't block deployment.
- Code coverage < 80%
- Missing type hints
- Inconsistent logging format

---

## Security Standards

### 1. Secrets Management

**Standard:** Zero secrets in source code, configuration files, or container images.

**Approved Methods:**
- Environment variables (development/staging)
- Kubernetes Secrets (production)
- HashiCorp Vault (highly sensitive)
- Cloud provider secret managers (AWS Secrets Manager, Azure Key Vault)

**Detection:**
- Automated secret scanning in CI/CD (detect-secrets, trufflehog)
- Pre-commit hooks to prevent accidental commits
- Regular repository scans

**Specification:** `specs/security/secrets_management.spec`

---

### 2. SQL Injection Prevention

**Standard:** 100% parameterized queries for all database operations.

**Approved Libraries:**
- psycopg2 (PostgreSQL) - with parameterized queries
- SQLAlchemy ORM - with query builder (NOT raw SQL)
- Django ORM - built-in protection

**Forbidden Practices:**
- String formatting in SQL queries (f-strings, %, +)
- Dynamic table/column names from user input
- Raw SQL execution without parameterization

**Detection:**
- Static code analysis (Bandit, Semgrep)
- Security-focused unit tests
- Mandatory security code review

**Specification:** `specs/security/sql_injection_prevention.spec`

---

### 3. Dependency Management

**Standard:** All dependencies pinned to specific versions and scanned for vulnerabilities.

**Requirements:**
- Pin all packages with `==` in requirements.txt
- Run `pip-audit` in CI/CD pipeline
- Update dependencies monthly (security patches)
- Document dependency approval in SBOM

**Approved Package Sources:**
- PyPI (default, verify package authenticity)
- Internal artifact repository (preferred for production)

**Blocklist:**
- Packages with CRITICAL CVEs
- Unmaintained packages (no updates > 2 years)
- Packages with unclear licensing

**Specification:** `specs/security/dependency_management.spec`

---

### 4. Container Security

**Standard:** Use approved base images, run as non-root, minimize attack surface.

**Approved Base Images:**
```
python:3.11-slim-bookworm
python:3.12-slim-bookworm
```

**Required Dockerfile Practices:**
- Multi-stage builds (separate build and runtime)
- Non-root user (UID 1000+)
- No secrets in layers
- Minimal installed packages
- Health checks defined
- Vulnerability scanning with Trivy/Snyk

**Specification:** `specs/deployment/dockerfile.spec`

---

### 5. Web Application Security (OWASP Top 10)

**Standard:** Implement controls for OWASP Top 10 vulnerabilities.

| Vulnerability | Required Control |
|---------------|------------------|
| A01: Broken Access Control | Role-based authorization, principle of least privilege |
| A02: Cryptographic Failures | TLS 1.2+, secure session cookies, no plaintext secrets |
| A03: Injection | Parameterized queries, input validation, output encoding |
| A04: Insecure Design | Threat modeling, security requirements in design |
| A05: Security Misconfiguration | Security headers, secure defaults, disable debug in prod |
| A06: Vulnerable Components | Dependency scanning, SBOM generation, regular updates |
| A07: Auth Failures | Multi-factor auth (where applicable), secure session mgmt |
| A08: Software/Data Integrity | Code signing, SBOM verification, secure CI/CD |
| A09: Logging Failures | Security event logging, log monitoring, tamper protection |
| A10: SSRF | Validate URLs, whitelist allowed hosts, network segmentation |

**Specification:** `specs/security/web_security.spec`

---

## Architecture Standards

### 1. Database Layer

**Standard:** Centralized, secure database connection management with connection pooling.

**Requirements:**
- Connection pooling (psycopg2.pool or equivalent)
- Context managers for connection lifecycle
- Prepared statements for all queries
- Read-only database users where applicable
- Connection timeout configuration
- Retry logic with exponential backoff

**Specification:** `specs/architecture/database_layer.spec`

---

### 2. Application Structure

**Standard:** Consistent project structure for maintainability.

```
project/
├── src/                    # Application source code
│   ├── __init__.py
│   ├── app.py             # Application entry point
│   ├── config.py          # Configuration management
│   ├── database.py        # Database layer
│   ├── routes.py          # HTTP endpoints
│   └── templates/         # UI templates
├── tests/                 # Test suite
│   ├── test_security.py   # Security tests (REQUIRED)
│   └── test_app.py        # Functional tests
├── config/                # Configuration files
│   └── .env.example       # Example environment variables
├── specs/                 # Implementation specifications
├── docs/                  # Documentation
├── requirements.txt       # Pinned dependencies
├── Dockerfile             # Container definition
├── .gitlab-ci.yml        # CI/CD pipeline
└── CLAUDE.md             # AI development guidelines
```

**Specification:** `specs/architecture/web_application.spec`

---

## Testing Standards

### 1. Security Testing

**Standard:** Security tests MUST pass before deployment.

**Required Test Coverage:**
- SQL injection prevention (parameterized query verification)
- XSS prevention (output escaping verification)
- CSRF protection (token validation)
- Secret management (no hardcoded credentials)
- Input validation (whitelist verification)
- Security headers (presence and correctness)
- Authentication/authorization logic

**Test Framework:** pytest with pytest-cov

**Minimum Coverage:** 100% of security-critical code paths

**Specification:** `specs/testing/security_tests.spec`

---

### 2. Integration Testing

**Standard:** Test database connectivity, external APIs, and system integration.

**Requirements:**
- Test against real database (not mocks, where feasible)
- Test connection pool exhaustion scenarios
- Test timeout and retry logic
- Test error handling and recovery

---

## Deployment Standards

### 1. CI/CD Pipeline

**Standard:** Automated security scanning in every pipeline run.

**Required Stages:**
1. **Security Scan** (blocking)
   - Secret detection (detect-secrets)
   - SBOM generation (cyclonedx-bom)
   - Dependency scanning (pip-audit)
   
2. **Test** (blocking)
   - Unit tests (pytest)
   - Security tests (pytest)
   - Coverage report (minimum 80%)

3. **Build** (blocking)
   - Container build
   - Container scanning (Trivy)
   - Image signing

4. **Deploy** (manual approval)
   - Staging deployment
   - Production deployment (requires approval)

**Specification:** `specs/deployment/ci_cd_pipeline.spec`

---

### 2. Environment Configuration

**Standard:** Environment-specific configuration with secure secret injection.

**Environments:**
- **Development:** Local `.env` files, relaxed security for debugging
- **Staging:** Kubernetes Secrets, mirrors production security
- **Production:** Vault/Secrets Manager, full security controls

**Configuration Sources (priority order):**
1. Environment variables (highest priority)
2. Kubernetes ConfigMaps/Secrets
3. Vault/Secrets Manager
4. Default values in code (non-sensitive only)

---

## Monitoring & Compliance

### 1. Security Event Logging

**Standard:** Log all security-relevant events with structured format.

**Required Log Events:**
- Authentication attempts (success/failure)
- Authorization failures
- Input validation failures
- Database connection errors
- Unhandled exceptions

**Log Format:** JSON with timestamp, severity, event type, user context

---

### 2. Vulnerability Management

**Standard:** Regular scanning and remediation of vulnerabilities.

**Process:**
- Weekly automated scans (dependencies, containers)
- Monthly manual security review
- CRITICAL CVEs remediated within 7 days
- HIGH CVEs remediated within 30 days
- Quarterly penetration testing

---

## Approved Technology Stack

### Python Versions
- **Approved:** 3.11.x, 3.12.x (active security support)
- **Deprecated:** 3.10.x and older (end of support)

### Web Frameworks
- **Approved:** Flask 3.x, Django 4.x, FastAPI 0.1xx
- **Required:** Latest stable minor version

### Database Drivers
- **PostgreSQL:** psycopg2-binary 2.9.x, asyncpg
- **MySQL:** mysql-connector-python 8.x
- **SQLite:** Built-in (development only)

### Container Base Images
- **Approved:** Red Hat UBI 9 Python images
  - registry.access.redhat.com/ubi9/python-311:latest
  - registry.access.redhat.com/ubi9/python-39:latest
- **Forbidden:** alpine (compatibility issues), latest (non-UBI), EOL versions, non-Red Hat images

### Testing
- **Framework:** pytest 8.x
- **Coverage:** pytest-cov
- **Security:** bandit, safety, pip-audit

---

## Exceptions & Waivers

**Process:**
1. Document exception request with business justification
2. Risk assessment by security team
3. Compensating controls identified
4. CISO approval required for CRITICAL/REQUIRED violations
5. Documented in project README with expiration date

**Valid Exception Reasons:**
- Technical constraint (e.g., legacy system integration)
- Performance requirement (with evidence)
- Temporary waiver with remediation plan

**Invalid Exception Reasons:**
- "Too difficult to implement"
- "Don't have time"
- "It worked before"

---

## Enforcement

### Pre-Commit
- Secret detection hooks
- Linting (flake8, black)
- Type checking (mypy)

### CI/CD Pipeline
- All security scans (blocking)
- Test suite execution (blocking)
- Coverage requirements (blocking)

### Code Review
- Mandatory security review for database code
- Mandatory senior engineer review for auth/authz
- Automated review comments for common issues

### Production Deployment
- Final security scan
- SBOM submission to vulnerability management system
- Deployment approval by platform team

---

## References

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CWE Top 25: https://cwe.mitre.org/top25/
- NIST Secure Software Development Framework
- Company Security Policy (internal)

---

## Version History

- **2.0** (2026-06-10): Added SBOM requirements, updated Python versions
- **1.5** (2025-09-15): Added container security standards
- **1.0** (2024-06-01): Initial release

---

**This document is the authoritative source for Python application standards.**  
**When specifications conflict with this document, this document takes precedence.**
