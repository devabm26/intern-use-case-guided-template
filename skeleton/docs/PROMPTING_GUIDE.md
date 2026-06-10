# AI-Assisted Development: Prompting Guide

**How to get secure, compliant code from AI assistants (Claude Code, GitHub Copilot, etc.)**

---

## 🎯 The Problem

Without guidance, AI assistants often generate insecure code:
- ❌ Hardcoded credentials
- ❌ SQL injection vulnerabilities
- ❌ Missing security controls
- ❌ Using deprecated packages

This project has **built-in guardrails** to prevent this, but you need to prompt correctly.

---

## ✅ The Solution: Specification-First Prompting

Instead of asking for code directly, **point the AI to the specifications**.

---

## 📖 Prompting Patterns

### ❌ BAD PROMPT (Vague, No Context)

```
Build me a database connection layer for PostgreSQL
```

**Problem:** AI will use generic patterns from training data, which may be insecure.

**Result:** Likely gets hardcoded credentials, no connection pooling, vulnerable to SQL injection.

---

### ✅ GOOD PROMPT (Specification-Driven)

```
I need to implement a database connection layer for PostgreSQL.

IMPORTANT: This is an enterprise application with mandatory security compliance.
Before writing code:
1. Read specs/architecture/database_layer.spec
2. Read specs/security/secrets_management.spec
3. Read specs/security/sql_injection_prevention.spec

Implement following those specifications exactly. Use:
- Connection pooling (psycopg2.pool)
- Environment variables for credentials (no hardcoding)
- Parameterized queries only
- Context managers for connection lifecycle

After implementation, create security tests per specs/testing/security_tests.spec
```

**Result:** AI reads specs, follows approved patterns, generates compliant code.

---

## 🎨 Template Prompts (Copy & Paste)

### For Database Implementation

```
I need to implement database connectivity.

MANDATORY READING:
- specs/architecture/database_layer.spec
- specs/security/sql_injection_prevention.spec
- specs/security/secrets_management.spec

REQUIREMENTS:
- Use connection pooling
- Load credentials from environment (NO hardcoding)
- All queries must be parameterized
- Include security tests

Follow the specifications exactly. Show me what you'll implement first.
```

---

### For Web Application Routes

```
I need to create web application routes/endpoints.

MANDATORY READING:
- specs/architecture/web_application.spec
- specs/security/web_security.spec
- CLAUDE.md (security requirements)

REQUIREMENTS:
- CSRF protection enabled
- Security headers configured
- Input validation with whitelisting
- Output encoding (XSS prevention)
- Include security tests

Follow the specifications. Describe your approach first.
```

---

### For Dockerfile

```
I need to create a production Dockerfile.

MANDATORY READING:
- specs/deployment/dockerfile.spec
- CLAUDE.md (approved base images)

REQUIREMENTS:
- Use Red Hat UBI: registry.access.redhat.com/ubi9/python-311:latest
- Multi-stage build
- Run as non-root (UID 1001)
- NO secrets in any layer
- Health check configured

Follow the specification exactly.
```

---

### For Adding Dependencies

```
I need to add [PACKAGE_NAME] to the project.

MANDATORY READING:
- specs/security/dependency_management.spec

REQUIREMENTS:
- Pin version with ==
- Check for CVEs: pip-audit
- Verify package is necessary
- Update requirements.txt
- Document why it's needed

Follow the dependency approval process in the spec.
```

---

## 🤖 Claude Code Specific Tips

If using **Claude Code** (this tool!), I automatically read `.claude/project-instructions.md` when you open the project.

### Best Practice Flow:

1. **Open project** → I load `.claude/project-instructions.md`
2. **Describe task** → I'll tell you which specs apply
3. **Confirm approach** → I'll summarize my implementation plan
4. **I implement** → Following specifications
5. **I create tests** → Security tests included
6. **You review** → Check my work aligns with requirements

### Example Conversation:

**You:**
```
I need to add a feature that displays user comments from the database
```

**Me (Claude):**
```
I'll implement this following our security specifications:

Reading:
- specs/architecture/database_layer.spec
- specs/security/sql_injection_prevention.spec
- specs/security/web_security.spec

My approach:
1. Create query function with parameterized statement
2. Add route with input validation
3. Template with auto-escaped output (XSS prevention)
4. Security tests for SQL injection & XSS

Shall I proceed?
```

**You:**
```
Yes, proceed
```

**Me:** _(implements with specifications compliance)_

---

## 🔄 Iterative Prompting

If the AI doesn't follow specs on first try:

### Redirect to Specifications

```
That code doesn't follow our security specifications.

Please read specs/security/sql_injection_prevention.spec and reimplement.
The query must use parameterized statements with %s placeholders.
```

### Ask for Verification

```
Before you implement, tell me:
1. Which specification files apply to this task?
2. What are the key security requirements?
3. What tests will you write?
```

---

## 📋 Verification Prompts

After implementation, verify compliance:

```
Review your implementation against these checklists:

1. Run security scans:
   - detect-secrets scan --all-files
   - pip-audit -r requirements.txt
   - pytest tests/test_security.py

2. Verify:
   - No hardcoded credentials?
   - All SQL queries parameterized?
   - Security headers configured?
   - Input validation present?

Show me the scan results.
```

---

## 🎓 Teaching the AI

First time working with an AI in this project:

```
This is an enterprise Python project with mandatory security compliance.

Key files you MUST read before coding:
1. .claude/project-instructions.md (automatic requirements)
2. CLAUDE.md (security rules)
3. specs/ directory (implementation specifications)

From now on, for every task:
1. Read applicable specs first
2. Tell me which specs apply
3. Describe your approach
4. Wait for my approval
5. Then implement

Let's start: I need to implement [TASK]
```

---

## 🚫 Anti-Patterns (What NOT to Do)

### ❌ Generic Prompts
```
Write a Flask app with database
```

### ❌ Asking to Skip Security
```
Just get it working quickly, we'll secure it later
```

### ❌ Not Referencing Specs
```
Build this however you think is best
```

### ❌ Accepting Non-Compliant Code
```
That's fine, let's move on
# (when AI generated hardcoded credentials)
```

---

## ✅ Best Practices Summary

### DO:
- ✅ Reference specification files in prompts
- ✅ Ask AI to read specs before coding
- ✅ Request implementation plan first
- ✅ Verify security tests are included
- ✅ Run scans after implementation
- ✅ Redirect to specs if code is non-compliant

### DON'T:
- ❌ Give vague prompts
- ❌ Skip specification reading
- ❌ Accept insecure code
- ❌ Skip security tests
- ❌ Trust without verification

---

## 🎯 Expected Outcome

With proper prompting:
- ✅ AI reads specifications before coding
- ✅ AI follows approved security patterns
- ✅ AI generates security tests automatically
- ✅ Code passes all security gates
- ✅ Deployment succeeds without manual fixes

**Remember:** The specifications are your contract with the AI. Point to them explicitly!

---

## 📚 Quick Reference

| Task Type | Specs to Reference | Key Phrase to Use |
|-----------|-------------------|-------------------|
| Database | `database_layer.spec`, `sql_injection_prevention.spec` | "Use parameterized queries" |
| Web Routes | `web_application.spec`, `web_security.spec` | "Enable CSRF, validate input" |
| Container | `dockerfile.spec` | "Use Red Hat UBI, non-root" |
| Dependencies | `dependency_management.spec` | "Pin versions, scan CVEs" |
| Any Task | `.claude/project-instructions.md`, `CLAUDE.md` | "Follow security specifications" |

---

**Pro Tip:** Treat AI assistants like junior developers who need clear requirements and specifications. The better your prompts, the better the code!
