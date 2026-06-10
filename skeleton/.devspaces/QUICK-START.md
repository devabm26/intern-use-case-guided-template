# ⚡ Quick Start: OpenShift Dev Spaces + Vertex AI Claude

**5-Minute Setup for Secure AI-Assisted Development**

---

## ✅ Prerequisites Checklist

- [ ] OpenShift Dev Spaces workspace launched
- [ ] Access to Vertex AI Claude (Google Cloud)
- [ ] Project cloned in Dev Spaces
- [ ] Terminal open in Dev Spaces

---

## 🚀 Step 1: First-Time Setup (2 minutes)

```bash
# Make scripts executable
chmod +x .devspaces/load-context.sh

# Install development dependencies
pip install -r requirements.txt

# Install security scanning tools
pip install detect-secrets pip-audit bandit cyclonedx-bom
```

---

## 🤖 Step 2: Load AI Context (Every Session)

### In Dev Spaces Terminal:
```bash
# Run context loader
./.devspaces/load-context.sh
```

### Copy Output → Paste to Vertex AI Claude

**In Vertex AI Claude chat, start with:**
```
[PASTE ENTIRE OUTPUT FROM load-context.sh]

I'm ready to start development. I understand I must:
1. Read applicable specs before coding
2. Follow ✅ APPROVED patterns only
3. Avoid ❌ FORBIDDEN patterns
4. Write security tests

Ready for tasks!
```

---

## 💻 Step 3: Development Workflow

### For Each Feature:

**1. Prompt Claude (with spec reference):**
```
I need to implement [YOUR TASK].

MANDATORY: Read specs/[relevant-spec].spec first.

Requirements:
- [KEY REQUIREMENT 1]
- [KEY REQUIREMENT 2]

Describe your approach before implementing.
```

**2. Claude implements → You copy code to Dev Spaces**

**3. Test locally:**
```bash
# Run security tests
pytest tests/test_security.py -v

# Check for secrets
detect-secrets scan --all-files

# Scan dependencies
pip-audit -r requirements.txt
```

**4. If tests pass → Commit & push**

---

## 📋 Common Tasks Cheat Sheet

### Database Implementation
```
Task: Implement database connectivity

Specs to read:
- specs/architecture/database_layer.spec
- specs/security/sql_injection_prevention.spec
- specs/security/secrets_management.spec

Key requirements:
- Connection pooling (psycopg2.pool)
- Environment variables (no hardcoding)
- Parameterized queries only
```

### Web Routes
```
Task: Create web endpoint

Specs to read:
- specs/architecture/web_application.spec
- specs/security/web_security.spec

Key requirements:
- CSRF protection enabled
- Input validation (whitelist)
- Output escaping (XSS prevention)
- Security headers configured
```

### Dockerfile
```
Task: Create production Dockerfile

Specs to read:
- specs/deployment/dockerfile.spec

Key requirements:
- Red Hat UBI base: registry.access.redhat.com/ubi9/python-311:latest
- Multi-stage build
- Non-root user (UID 1001)
- No secrets in image
```

---

## 🔍 Verification Commands

```bash
# Quick security check (run before committing)
pytest tests/test_security.py && \
detect-secrets scan --all-files && \
pip-audit -r requirements.txt && \
echo "✅ All checks passed!"

# Build and scan container
podman build -t myapp:latest . && \
trivy image --severity HIGH,CRITICAL myapp:latest

# Generate SBOM
cyclonedx-py requirements -r requirements.txt -o sbom.json
```

---

## 🆘 Troubleshooting

### Claude Generated Insecure Code

**Problem:** Hardcoded credentials or SQL injection

**Fix:**
```
Claude, that code violates specs/security/[SPEC_NAME].spec

Please reimplement following the ✅ APPROVED pattern:
[PASTE APPROVED PATTERN FROM SPEC]
```

### Tests Failing

**Problem:** Security tests fail after implementation

**Fix:**
```bash
# See what failed
pytest tests/test_security.py -v

# Common issues:
# 1. Hardcoded secret → Use os.environ.get()
# 2. String formatting in SQL → Use parameterized query
# 3. Missing security header → Add in @app.after_request
```

Then tell Claude:
```
The test [TEST_NAME] failed with: [ERROR]
Fix the code to pass this test.
```

### Context Too Long

**Problem:** Context + prompt exceeds token limit

**Solution:**
```
# Load context ONCE per session
[Paste full context first time only]

# Then for each task:
"Implement [TASK]. Read specs/[SPEC].spec. Requirements: [KEY POINTS]"
```

---

## 📚 Reference Materials

| Resource | Location | When to Use |
|----------|----------|-------------|
| **Full Dev Spaces Guide** | `.devspaces/README-DEVSPACES.md` | Detailed workflow |
| **Prompting Templates** | `docs/PROMPTING_GUIDE.md` | Example prompts |
| **Security Rules** | `CLAUDE.md` | Absolute requirements |
| **Standards Doc** | `docs/ENTERPRISE_STANDARDS.md` | Full compliance guide |
| **Compliance Matrix** | `../COMPLIANCE_MECHANISMS.md` | How enforcement works |

---

## ⏱️ Typical Session (10 minutes)

```
Minute 0-2:   Load context (.devspaces/load-context.sh)
Minute 2-3:   Paste to Vertex AI Claude
Minute 3-7:   Claude implements feature
Minute 7-9:   Run security tests locally
Minute 9-10:  Commit & push (CI/CD validates)
```

---

## ✅ Success Checklist

Before marking task complete:

- [ ] Loaded context at session start
- [ ] Referenced applicable specs in prompt
- [ ] Claude described approach (approved it)
- [ ] Code copied to Dev Spaces
- [ ] Security tests pass (`pytest tests/test_security.py`)
- [ ] No secrets detected (`detect-secrets scan`)
- [ ] No CVEs found (`pip-audit`)
- [ ] Code committed and pushed
- [ ] CI/CD pipeline passes

---

## 🎯 Remember

1. **Load context FIRST** - Run `.devspaces/load-context.sh` at session start
2. **Reference specs** - Always point Claude to specific spec files
3. **Test locally** - Don't skip security tests
4. **Trust CI/CD** - It will catch what you miss

**You are the bridge between specs and Claude. Load context, reference specs, validate locally!**

---

**Need help?** See `.devspaces/README-DEVSPACES.md` for complete documentation.
