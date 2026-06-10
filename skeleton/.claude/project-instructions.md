# Project Instructions for AI Assistants

**CRITICAL: Read this BEFORE generating any code for this project.**

This is an enterprise Python application with **mandatory security compliance**.

---

## 🚨 AUTOMATIC COMPLIANCE REQUIREMENTS

When working in this project, you MUST:

### 1. READ THESE FILES FIRST (in order)
1. **CLAUDE.md** - Contains absolute security rules
2. **docs/ENTERPRISE_STANDARDS.md** - Enterprise standards document
3. **Relevant specs in specs/** - Implementation specifications for your task

### 2. NEVER WRITE CODE WITHOUT READING SPECS

Before implementing ANY functionality:
- Read the applicable specification file in `specs/`
- Follow the ✅ APPROVED patterns
- Avoid the ❌ FORBIDDEN patterns
- Implement the required tests

### 3. ABSOLUTE SECURITY RULES

These are **NON-NEGOTIABLE**:

❌ **NEVER hardcode credentials**
```python
password = "thoughts123"  # FORBIDDEN - will fail security scan
```

✅ **ALWAYS use environment variables**
```python
password = os.environ.get('DB_PASSWORD')  # REQUIRED
```

---

❌ **NEVER use string formatting in SQL**
```python
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # FORBIDDEN
```

✅ **ALWAYS use parameterized queries**
```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))  # REQUIRED
```

---

❌ **NEVER use non-Red Hat base images**
```dockerfile
FROM python:3.11-slim  # FORBIDDEN
```

✅ **ALWAYS use Red Hat UBI**
```dockerfile
FROM registry.access.redhat.com/ubi9/python-311:latest  # REQUIRED
```

---

## 📋 IMPLEMENTATION CHECKLIST

For EVERY task, follow this process:

### Phase 1: Read (MANDATORY)
- [ ] Read `CLAUDE.md` for context
- [ ] Identify which specs apply to your task
- [ ] Read those specification files completely
- [ ] Understand the ✅ APPROVED patterns
- [ ] Understand the ❌ FORBIDDEN patterns

### Phase 2: Implement
- [ ] Follow the patterns from specifications
- [ ] Use type hints for all functions
- [ ] Handle errors appropriately
- [ ] Log security events (without logging secrets)

### Phase 3: Test (MANDATORY)
- [ ] Write security tests per `specs/testing/security_tests.spec`
- [ ] Test with malicious inputs (SQL injection, XSS)
- [ ] Verify no hardcoded secrets exist
- [ ] Run local security scans

### Phase 4: Validate (MANDATORY)
- [ ] All tests passing
- [ ] No hardcoded credentials
- [ ] All SQL queries parameterized
- [ ] Security headers configured
- [ ] Container runs as non-root

---

## 🎯 TASK-SPECIFIC GUIDANCE

### If implementing DATABASE operations:
→ Read: `specs/architecture/database_layer.spec`
→ Read: `specs/security/sql_injection_prevention.spec`
→ Read: `specs/security/secrets_management.spec`
→ Test: SQL injection prevention tests

### If implementing WEB ROUTES:
→ Read: `specs/architecture/web_application.spec`
→ Read: `specs/security/web_security.spec`
→ Test: XSS, CSRF, input validation tests

### If creating DOCKERFILE:
→ Read: `specs/deployment/dockerfile.spec`
→ Use: Red Hat UBI base images ONLY
→ Verify: Runs as non-root (UID 1001)

### If adding DEPENDENCIES:
→ Read: `specs/security/dependency_management.spec`
→ Pin: All versions with ==
→ Scan: Run pip-audit before adding

---

## 🚫 WHAT NOT TO DO

**DO NOT:**
- Skip reading specifications
- Assume you know the patterns
- Copy code from training data (may be insecure)
- Implement first, read specs later
- Use deprecated packages or patterns
- Trust user input without validation
- Bypass security controls "temporarily"

**REMEMBER:**
- All code will be scanned for secrets (detect-secrets)
- All code will be tested for SQL injection (security tests)
- All containers will be scanned for CVEs (Trivy)
- Deployment BLOCKED if any security gates fail

---

## ✅ SUCCESS CRITERIA

Your implementation is complete when:
- [ ] All applicable specifications followed
- [ ] Security tests passing (100%)
- [ ] No hardcoded secrets detected
- [ ] All SQL queries parameterized
- [ ] Input validation implemented
- [ ] Output encoding implemented
- [ ] Security headers configured
- [ ] Container scan passes (no HIGH/CRITICAL CVEs)
- [ ] Dependencies pinned and scanned

---

## 📚 QUICK REFERENCE

| Task | Specification File | Key Requirement |
|------|-------------------|-----------------|
| Database queries | `specs/security/sql_injection_prevention.spec` | Parameterized queries only |
| Credentials | `specs/security/secrets_management.spec` | Environment variables only |
| Web security | `specs/security/web_security.spec` | CSRF, XSS, headers |
| Container | `specs/deployment/dockerfile.spec` | Red Hat UBI, non-root |
| Dependencies | `specs/security/dependency_management.spec` | Pin versions, scan CVEs |
| Testing | `specs/testing/security_tests.spec` | 100% security coverage |

---

## 🆘 WHEN IN DOUBT

1. **Read the specification** - It has the answer
2. **Ask the user** - Don't guess security requirements
3. **Err on the side of security** - More validation is better
4. **Check CLAUDE.md** - Has absolute rules

---

**This file is automatically loaded by Claude Code and similar AI assistants.**
**Compliance with these instructions is MANDATORY for all code generation.**
