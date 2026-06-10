---
name: security-scan
description: Run comprehensive security scans on the codebase
---

# Security Scan Skill

Runs all security validation checks before committing or deploying code.

## What This Skill Does

1. **Secret Detection** - Scans for hardcoded credentials
2. **Dependency Scanning** - Checks for known CVEs
3. **Static Analysis** - Finds security vulnerabilities in code
4. **SBOM Generation** - Creates software bill of materials

## When to Use

- Before committing code
- After adding new dependencies
- Before creating a pull request
- During code review

## Commands Executed

```bash
# 1. Scan for hardcoded secrets
detect-secrets scan --all-files --force-use-all-plugins

# 2. Check dependencies for CVEs
pip-audit -r requirements.txt --desc

# 3. Static security analysis
bandit -r src/ -ll -f json -o bandit-report.json

# 4. Generate SBOM
cyclonedx-py requirements -r requirements.txt -o sbom.json

# 5. Summary
echo "=== Security Scan Complete ==="
echo "Review results above for any failures."
```

## Expected Output

- ✅ **PASS**: No issues found - safe to commit
- ❌ **FAIL**: Issues detected - must fix before committing

## Common Failures & Fixes

### Secrets Detected
```
Fix: Remove hardcoded credentials
Use: os.environ.get('SECRET_NAME') instead
```

### CVEs Found
```
Fix: Update vulnerable package
Run: pip install --upgrade <package>
Check: specs/security/dependency_management.spec
```

### Security Issues in Code
```
Fix: Review bandit-report.json
Common: SQL injection, hardcoded passwords
Check: Applicable spec in specs/security/
```

## Integration

This skill is used by:
- Pre-commit hooks (if configured)
- CI/CD pipeline (mandatory gate)
- Local development workflow
