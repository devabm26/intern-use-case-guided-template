---
name: spec-validator
description: Validate that code follows enterprise security specifications
---

# Specification Validator Skill

Checks if implemented code complies with specifications in `specs/` directory.

## What This Skill Does

Validates code against mandatory requirements from specification files:
- Database code → `specs/architecture/database_layer.spec`
- SQL queries → `specs/security/sql_injection_prevention.spec`
- Credentials → `specs/security/secrets_management.spec`
- Web routes → `specs/security/web_security.spec`
- Dockerfile → `specs/deployment/dockerfile.spec`

## When to Use

- After implementing new features
- Before code review
- When security tests fail
- During refactoring

## Validation Checks

### 1. Database Layer Validation
```bash
# Check for parameterized queries
grep -r "cursor.execute.*f\"" src/ && echo "FAIL: F-string in SQL" || echo "PASS"
grep -r "cursor.execute.*+" src/ && echo "FAIL: String concat in SQL" || echo "PASS"

# Check for connection pooling
grep -r "psycopg2.pool" src/ || echo "WARNING: No connection pooling found"
```

### 2. Secrets Management Validation
```bash
# Check for hardcoded credentials
grep -rE "(password|secret|key)\s*=\s*['\"][^'\"]+['\"]" src/ \
  && echo "FAIL: Hardcoded credentials found" || echo "PASS"

# Check for environment variable usage
grep -r "os.environ.get" src/ || echo "WARNING: No env var usage found"
```

### 3. Web Security Validation
```bash
# Check for CSRF protection
grep -r "CSRFProtect" src/ || echo "WARNING: CSRF protection not found"

# Check for security headers
grep -r "after_request" src/ || echo "WARNING: Security headers not configured"
```

### 4. Container Security Validation
```bash
# Check for approved base images
grep "FROM registry.access.redhat.com/ubi9/python" Dockerfile \
  || echo "FAIL: Not using approved Red Hat UBI base image"

# Check for non-root user
grep "USER 1001" Dockerfile || echo "FAIL: Not running as non-root user"
```

### 5. Dependency Security Validation
```bash
# Check for pinned versions
grep -E "^[a-zA-Z0-9_-]+==\d" requirements.txt \
  || echo "WARNING: Not all dependencies pinned with =="
```

## Expected Output

```
=== Specification Validation Results ===

Database Layer:         ✅ PASS
Secrets Management:     ✅ PASS
Web Security:          ⚠️  WARNING - Missing CSRF
Container Security:     ✅ PASS
Dependency Management:  ✅ PASS

Overall: 4/5 checks passed
Action Required: Configure CSRF protection per specs/security/web_security.spec
```

## How to Fix Failures

Each failure message references the applicable specification:

```
FAIL: Hardcoded credentials found
→ Fix: Read specs/security/secrets_management.spec
→ Replace: password = "literal" 
→ With: password = os.environ.get('DB_PASSWORD')
```

## Integration

- Run manually: `./scripts/validate-specs.sh`
- CI/CD stage: Part of test suite
- Pre-commit: Optional hook
