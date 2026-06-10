# Using This Template with OpenShift Dev Spaces + Vertex AI Claude

**Environment:** Red Hat OpenShift Dev Spaces + Claude via Google Vertex AI

---

## 🔴 Important: Manual Context Loading Required

Unlike **Claude Code CLI**, Vertex AI Claude does **NOT** automatically read `.claude/project-instructions.md`. You must manually provide context in each AI session.

---

## ⚙️ Initial Configuration

### Configure OpenCode Installation (One-Time)

**Before using the template, update `.devfile.yaml`:**

1. Open `.devfile.yaml`
2. Find the `install-opencode` command
3. Replace the placeholder with your actual OpenCode installation method:

```yaml
# Example if OpenCode is a downloadable binary:
curl -fsSL https://your-opencode-url.com/opencode -o /usr/local/bin/opencode && \
chmod +x /usr/local/bin/opencode

# Example if OpenCode is a Python package:
pip install opencode-cli

# Example if OpenCode is an RPM package:
dnf install -y opencode-cli
```

---

## 🚀 Quick Start Workflow

### Step 1: Load Project Context (Once per Session)

When starting a new Dev Spaces workspace:

```bash
# Make script executable
chmod +x .devspaces/load-context.sh

# Run context loader
./.devspaces/load-context.sh
```

**Copy the entire output** and paste it into your **first prompt** to Claude (via Vertex AI).

---

### Step 2: Use Template Prompts

For each task, use prompts from `docs/PROMPTING_GUIDE.md`.

**Example:**
```
[Paste context from load-context.sh]

Now, I need to implement database connectivity for PostgreSQL.

MANDATORY: Read these specifications first:
- specs/architecture/database_layer.spec
- specs/security/sql_injection_prevention.spec
- specs/security/secrets_management.spec

Requirements:
- Connection pooling (psycopg2.pool)
- Load credentials from environment (NO hardcoding)
- Parameterized queries only
- Include security tests

Describe your approach before implementing.
```

---

### Step 3: Verify Compliance

After Claude generates code:

```bash
# Check for hardcoded secrets
pip install detect-secrets
detect-secrets scan --all-files

# Run security tests
pytest tests/test_security.py -v

# Scan dependencies
pip install pip-audit
pip-audit -r requirements.txt
```

---

## 📋 Dev Spaces Specific Setup

### Terminal Commands Available

```bash
# Load compliance context (run first)
./.devspaces/load-context.sh

# View specification files
cat specs/security/sql_injection_prevention.spec
cat specs/architecture/database_layer.spec

# Run security scans
./scripts/security-scan.sh

# Run tests
pytest tests/test_security.py -v
```

---

## 🎯 Recommended Workflow

### Session Start (Do This First!)

1. **Open Dev Spaces workspace**
2. **Run context loader:**
   ```bash
   ./.devspaces/load-context.sh > /tmp/context.txt
   cat /tmp/context.txt
   ```
3. **Copy entire output**
4. **Paste into first Claude prompt** (via Vertex AI)
5. Claude now has project context ✅

---

### For Each Task

1. **Describe task + reference specs**
   ```
   I need to [TASK].
   
   Read specs/[relevant-spec].spec first.
   Requirements: [KEY_REQUIREMENTS]
   ```

2. **Claude reads spec and implements**

3. **Verify locally:**
   ```bash
   pytest tests/test_security.py -v
   detect-secrets scan --all-files
   ```

4. **Commit and push** → CI/CD validates

---

## ⚙️ Dev Spaces Configuration

### Environment Variables (Set in Dev Spaces)

Configure these in your Dev Spaces workspace:

```bash
# Database (for local testing)
export DB_HOST=postgresql.namespace.svc.cluster.local
export DB_NAME=app_database
export DB_USER=app_user
export DB_PASSWORD=<from-openshift-secret>

# Flask
export SECRET_KEY=<generate-with-python-secrets>
export FLASK_ENV=development
```

### Pre-installed Tools

The `.devfile.yaml` ensures these are available:

- ✅ Python 3.11+
- ✅ PostgreSQL client
- ✅ Security scanning tools (detect-secrets, pip-audit, bandit)
- ✅ Testing tools (pytest, pytest-cov)
- ✅ Container tools (podman)

---

## 🔍 Troubleshooting

### Claude Generates Insecure Code

**Problem:** Claude created hardcoded credentials or SQL injection vulnerability

**Solution:**
1. You forgot to load context or reference specs
2. Re-run `.devspaces/load-context.sh`
3. Paste context + specific spec references
4. Ask Claude to re-implement

**Example Fix Prompt:**
```
That code violates our security specifications.

Please read specs/security/secrets_management.spec and reimplement.
ALL credentials MUST come from environment variables using os.environ.get().
NO hardcoded values allowed.
```

---

### Context Too Long for One Prompt

**Problem:** Full context + task exceeds token limit

**Solution:** Load context once per session, then just reference specs:

```
Session Start:
  [Paste full context from load-context.sh]

Subsequent Tasks:
  "Implement [TASK].
   Read specs/[specific-spec].spec.
   Requirements: [KEY_POINTS]"
```

---

### Tests Fail After AI Generation

**Problem:** Security tests fail even though Claude "followed specs"

**Solution:** Trust the tests, not the AI claim:

```bash
# See what failed
pytest tests/test_security.py -v

# Fix the specific violation
# Common issues:
# - Hardcoded secret found
# - Non-parameterized query
# - Missing security header
```

Then:
```
Claude, the test test_sql_injection_prevention failed.
The query at line 42 uses string formatting.
Fix it to use parameterized query with %s placeholder.
```

---

## 📊 Compliance Workflow Diagram

```
┌─────────────────────────────────────────────┐
│ Start Dev Spaces Workspace                  │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ Run: ./.devspaces/load-context.sh           │
│ Copy output to clipboard                    │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ Open Vertex AI Claude Chat                  │
│ Paste context + task description            │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ Claude reads specs → generates code         │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ Run local validation:                       │
│ - pytest tests/test_security.py             │
│ - detect-secrets scan                       │
└─────────────┬───────────────────────────────┘
              │
         PASS │  FAIL
              ▼      │
           Deploy   ├──> Fix issues
                    │    Ask Claude to correct
                    └────┘
```

---

## 🎓 Learning Path for Interns

### Week 1: Setup & Understanding
1. **Explore Dev Spaces workspace**
2. **Run `.devspaces/load-context.sh`** to see what Claude needs
3. **Read `docs/ENTERPRISE_STANDARDS.md`**
4. **Review each spec in `specs/security/`**
5. **Understand why each rule exists**

### Week 2: Practice with AI
1. **Start simple task** (e.g., "create health check endpoint")
2. **Load context, prompt Claude properly**
3. **Run security tests**
4. **Experience CI/CD blocking insecure code**
5. **Learn to fix common violations**

### Week 3: Build Real Feature
1. **Implement database layer** with Claude's help
2. **Add web routes** with proper security
3. **Write comprehensive tests**
4. **Deploy to staging OpenShift**
5. **Monitor in production**

---

## 💡 Pro Tips for Dev Spaces + Vertex AI

### Tip 1: Create Context Snippet
Save context as a snippet in Dev Spaces for quick access:
```bash
# Add to ~/.bashrc in Dev Spaces
alias load-ai-context='cat /tmp/context.txt'
```

### Tip 2: Use Terminal in Split View
- Left: Claude chat (Vertex AI)
- Right: Dev Spaces terminal for testing

### Tip 3: Iterative Prompting
Don't try to build everything in one prompt:
```
Prompt 1: "Implement database connection pool"
Prompt 2: "Now add query function for users table"
Prompt 3: "Add security tests for SQL injection"
```

### Tip 4: Reference Specific Spec Sections
```
Read specs/security/sql_injection_prevention.spec,
specifically the section on parameterized queries (REQ-1).
```

---

## 🔗 Additional Resources

- **Main README:** `../README.md`
- **Prompting Guide:** `docs/PROMPTING_GUIDE.md`
- **Compliance Mechanisms:** `../COMPLIANCE_MECHANISMS.md`
- **Enterprise Standards:** `docs/ENTERPRISE_STANDARDS.md`

---

## ✅ Success Checklist

Before considering a feature complete:

- [ ] Loaded context at session start
- [ ] Referenced applicable specs in prompts
- [ ] Claude generated code following specs
- [ ] All security tests pass locally
- [ ] No secrets detected by detect-secrets
- [ ] No CVEs found by pip-audit
- [ ] Code committed and pushed
- [ ] CI/CD pipeline passes all gates
- [ ] Deployed to staging successfully

---

**Remember:** In Dev Spaces + Vertex AI setup, **you are the bridge** between the template's specifications and Claude. Load context, reference specs explicitly, and trust the security tests!
