# Enterprise Python Application - Backstage Scaffolder Template

**Golden Path Template for Secure Python Web Applications (Red Hat Ready)**

## Overview

This Backstage scaffolder template generates Python web applications with **built-in security guardrails** that force LLMs (and developers) to follow enterprise security standards. It's designed to enable "vibe coding" while preventing common vulnerabilities through:

- **Comprehensive specifications** instead of boilerplate code
- **Security-by-default** patterns
- **Mandatory compliance gates** in CI/CD
- **AI-friendly documentation** (CLAUDE.md with strict rules)

---

## 🎯 Use Case: Guided Development with Security Guardrails

### Problem Statement
Without proper guardrails, fast-paced development can introduce common security vulnerabilities:
- Hardcoded credentials
- SQL injection vulnerabilities
- Missing CSRF protection
- Vulnerable dependencies
- Running containers as root

### Solution
This template provides **specifications instead of code**, forcing implementations to follow secure patterns:

```
❌ Traditional Template          ✅ This Template
├── src/app.py (code)           ├── specs/security/*.spec (rules)
├── src/database.py (code)      ├── specs/architecture/*.spec (patterns)
└── Dockerfile (insecure)       ├── CLAUDE.md (AI guardrails)
                                └── docs/ENTERPRISE_STANDARDS.md (standards)
```

### How It Works

1. **Developer/AI reads specifications** before writing code
2. **CLAUDE.md enforces rules** for AI-assisted development
3. **CI/CD pipeline validates compliance** (security scans, tests)
4. **Deployment blocked** if security gates fail

Result: Even "vibe coding" produces secure, compliant applications.

---

## 📁 Template Structure

```
intern-use-case-guided/
├── template.yaml                    # Backstage scaffolder definition
├── skeleton/                        # Generated project template
│   ├── specs/                       # IMPLEMENTATION SPECIFICATIONS
│   │   ├── security/
│   │   │   ├── secrets_management.spec
│   │   │   ├── sql_injection_prevention.spec
│   │   │   ├── web_security.spec
│   │   │   └── dependency_management.spec
│   │   ├── architecture/
│   │   │   ├── database_layer.spec
│   │   │   └── web_application.spec
│   │   ├── testing/
│   │   │   └── security_tests.spec
│   │   └── deployment/
│   │       ├── dockerfile.spec
│   │       └── ci_cd_pipeline.spec
│   ├── docs/
│   │   └── ENTERPRISE_STANDARDS.md   # Authoritative standards doc
│   ├── config/
│   │   └── .env.example              # Environment template
│   ├── requirements.txt              # Pinned dependencies
│   ├── Dockerfile                    # Secure container template
│   │   # Note: CI/CD config not included - implement per your platform
│   ├── CLAUDE.md                    # AI development rules
│   ├── README.md                    # Project README template
│   ├── catalog-info.yaml            # Backstage catalog entry
│   └── .gitignore                   # Security-aware ignores
└── README.md                        # This file
```

---

## ❓ FAQ: Does Compliance Happen Automatically?

**Q: When using AI to generate code, does the user need to say "comply with specs" or is it automatic?**

**A: It depends on the AI tool:**

| AI Tool | Compliance Level | User Action |
|---------|-----------------|-------------|
| **Claude Code** | 🟢 Semi-Automatic | Just describe task normally |
| **VS Code Extension** | 🟡 Depends on config | Verify or prompt explicitly |
| **Dev Spaces + Vertex AI** | 🔴 Manual | **Run `.devspaces/load-context.sh`** |
| **GitHub Copilot** | 🔴 Manual | **Must reference specs in prompt** |
| **ChatGPT** | 🔴 Manual | **Must reference specs in prompt** |

**Claude Code Example (Automatic):**
```
You: "Add database queries for user data"
Claude: [auto-reads specs, implements securely] ✅
```

**Generic AI Example (Must Prompt):**
```
❌ BAD: "Add database queries"
   → Generates insecure code

✅ GOOD: "Add database queries. Read specs/security/sql_injection_prevention.spec.
         Use parameterized queries only."
   → Generates secure code
```

**However:** Even if AI guidance fails, **automated testing + CI/CD** always enforce compliance:
- Security tests catch violations
- CI/CD scans block deployment
- **Nothing insecure reaches production**

📚 **See `COMPLIANCE_MECHANISMS.md` for complete explanation.**

---

## 🏢 Red Hat Enterprise Ready

This template uses **Red Hat Universal Base Images (UBI)** as the foundation:

### Why Red Hat UBI?
- **Enterprise Support**: Official Red Hat support and SLAs available
- **Security**: Regular security patches and CVE fixes from Red Hat
- **Compliance**: FIPS 140-2, Common Criteria certified
- **Free to Use**: No subscription required, freely redistributable
- **Non-Root by Default**: UBI Python images run as UID 1001
- **OpenShift Optimized**: Best performance on Red Hat OpenShift
- **No Auth Required**: Pull from registry.access.redhat.com without login

### Container Images Used
- `registry.access.redhat.com/ubi9/python-311:latest`
- `registry.access.redhat.com/ubi9/python-39:latest`

---

## 🔒 Security Guardrails

### Layer 1: Specifications (Preventive)
**Location:** `skeleton/specs/`

Detailed specifications that define:
- ✅ APPROVED patterns (with examples)
- ❌ FORBIDDEN patterns (with explanations)
- **Testing requirements** (how to verify)
- **Implementation checklists** (step-by-step)

**Example:** `specs/security/sql_injection_prevention.spec`
```
REQ-1: PARAMETERIZED QUERIES ONLY
  Rule: 100% of SQL queries MUST use parameterized statements

  ✅ COMPLIANT:
    cursor.execute("SELECT * FROM users WHERE email = %s", (user_email,))

  ❌ NON-COMPLIANT:
    cursor.execute(f"SELECT * FROM users WHERE email = '{user_email}'")
```

### Layer 2: AI Development Rules (Directive)
**Location:** `skeleton/CLAUDE.md`

Explicit instructions for AI coding assistants:
- **ABSOLUTE RULES** that cannot be violated
- **Decision trees** for implementation choices
- **Required reading order** (specs before coding)
- **Success criteria** (when is code complete?)

**Example:** From CLAUDE.md
```markdown
## CRITICAL: Standards Compliance is MANDATORY

**Before writing ANY code:**
1. Read `docs/ENTERPRISE_STANDARDS.md`
2. Review relevant specification files in `specs/`
3. Follow security patterns defined in `specs/security/`
```

### Layer 3: CI/CD Gates (Detective)
**Specification:** `specs/deployment/ci_cd_pipeline.spec`  
**Implementation:** Your CI/CD platform (GitLab CI, GitHub Actions, Tekton, etc.)

Automated enforcement in pipeline:
1. **Security Scan** (blocking)
   - Secret detection (detect-secrets)
   - Dependency CVE scan (pip-audit)
   - SBOM generation (cyclonedx-bom)
   - Static analysis (bandit)

2. **Test** (blocking)
   - Security tests (100% required)
   - Unit tests (80% coverage)

3. **Build** (blocking)
   - Container vulnerability scan (Trivy)
   - Zero HIGH/CRITICAL CVEs allowed

4. **Deploy** (manual approval)
   - Staging/Production gates

---

## 🚀 How to Use This Template

### Option 1: Via Backstage UI

1. Navigate to Backstage → **Create** → **Choose a template**
2. Select **"Secure Python Dashboard Generator"**
3. Fill in required parameters:
   - **Component ID**: Application name
   - **Owner**: Team or user
   - **Database Host**: PostgreSQL hostname
4. Click **"Create"** → Template generates secure project

### Option 2: Manual Usage

1. **Copy skeleton directory**
   ```bash
   cp -r skeleton/ my-new-app/
   cd my-new-app/
   ```

2. **Replace template variables**
   - Search/replace `${{ values.component_id }}` with your app name
   - Update `${{ values.owner }}`, `${{ values.description }}`, etc.

3. **Initialize git repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit from enterprise template"
   ```

4. **Configure environment**
   ```bash
   cp config/.env.example .env
   # Edit .env with actual configuration
   ```

5. **Read specifications before coding**
   ```bash
   # Start here:
   cat docs/ENTERPRISE_STANDARDS.md
   cat CLAUDE.md

   # Then read relevant specs:
   ls specs/security/
   ls specs/architecture/
   ```

6. **Implement following specifications**
   - Each spec file has implementation checklist
   - Follow ✅ APPROVED patterns
   - Avoid ❌ FORBIDDEN patterns

7. **Run security validation**
   ```bash
   # Check for secrets
   pip install detect-secrets
   detect-secrets scan --all-files

   # Scan dependencies
   pip install pip-audit
   pip-audit -r requirements.txt

   # Run security tests
   pytest tests/test_security.py -v
   ```

---

## ⚙️ How Compliance Works (Automatic vs Manual)

### 🟢 Automatic Compliance

**Claude Code** (Anthropic's official CLI):
- ✅ Automatically reads `.claude/project-instructions.md`
- ✅ Knows to read specs before implementing
- ✅ Follows security patterns by default
- ✅ Includes security tests automatically
- ⚠️ Still requires task-specific prompting

**Example with Claude Code:**
```bash
# You open the project
cd my-app

# Claude Code automatically loads .claude/project-instructions.md
# Just describe what you need:
You: "Add database query to get all users"

Claude: "I'll implement this following specs/security/sql_injection_prevention.spec
         Using parameterized queries with connection pooling..."
```

### 🟡 Semi-Automatic Compliance

**IDEs with Claude/Copilot Extensions** (VS Code, JetBrains):
- ⚠️ May or may not auto-load `.claude/` directory
- ⚠️ Depends on extension configuration
- 📝 **Recommended:** Reference specs explicitly in prompts

### 🔴 Manual Compliance Required

**ChatGPT, Generic Copilot, Other AI Tools**:
- ❌ Do NOT auto-load project instructions
- ❌ Will generate generic (often insecure) code
- 📝 **Required:** MUST reference specs in every prompt

**Example with Generic AI:**
```
❌ BAD: "Create a login endpoint"
   → Will generate hardcoded credentials, no CSRF protection

✅ GOOD: "Create a login endpoint.
         MANDATORY: Read specs/security/web_security.spec first.
         Requirements: CSRF protection, secure sessions, no hardcoded secrets."
   → Generates compliant code
```

### 📚 Prompting Guide

**For all tools**, see `docs/PROMPTING_GUIDE.md` for:
- ✅ Template prompts (copy & paste)
- ✅ Specification-first patterns
- ✅ Verification steps
- ✅ Common pitfalls to avoid

---

## 📋 Generated Project Workflow

### For Developers

1. **Clone generated repository**
2. **Read CLAUDE.md** (mandatory)
3. **Review specs/** for implementation requirements
4. **Implement following specifications** (not guessing)
5. **Write security tests** as you code
6. **Run local security scans** before committing
7. **Push to GitLab** → CI/CD validates compliance
8. **Fix any security failures** (gates are blocking)
9. **Deploy to staging** after all gates pass
10. **Deploy to production** with approval

### For AI-Assisted Development (Claude Code, Copilot, etc.)

The template is optimized for AI coding assistants with **automatic compliance mechanisms**:

#### 🤖 Automatic Compliance (Claude Code)
When using **Claude Code**, compliance is semi-automatic:
1. **`.claude/project-instructions.md`** is auto-loaded when project opens
2. Claude automatically knows to read specs before coding
3. Claude follows security patterns without being told
4. Still needs task-specific prompting (see below)

#### 📝 Manual Prompting (Other AI Tools)
For **GitHub Copilot, ChatGPT, or other AI assistants**, you must prompt explicitly:

**❌ BAD PROMPT (Will generate insecure code):**
```
Build a database connection layer
```

**✅ GOOD PROMPT (Forces compliance):**
```
Build a database connection layer.

MANDATORY: Read specs/architecture/database_layer.spec first.
Follow the specification exactly:
- Connection pooling required
- Environment variables for credentials (NO hardcoding)
- Parameterized queries only
```

**📖 See `docs/PROMPTING_GUIDE.md` for complete prompting patterns.**

#### 🔄 Workflow
1. **User prompts** → References specification files
2. **AI reads specs/** for implementation patterns
3. **AI generates code** following specifications
4. **AI writes security tests** per testing spec
5. **Human reviews** for business logic correctness
6. **CI/CD validates** for security compliance

**Key Insight:** Specifications are more effective than code examples for constraining AI behavior, but you must **reference them in your prompts**.

---

## 🎓 Educational Use: Intern Onboarding

This template is ideal for onboarding junior developers:

### Learning Path

**Week 1: Understanding Security**
- Read `docs/ENTERPRISE_STANDARDS.md`
- Review each specification in `specs/security/`
- Run security scans on example vulnerable code
- Learn why each rule exists

**Week 2: Secure Implementation**
- Generate new project from template
- Implement database layer following `database_layer.spec`
- Write security tests following `security_tests.spec`
- Experience CI/CD gates blocking bad code

**Week 3: Full Application**
- Build complete web application
- Follow all specifications
- Pass all security gates
- Deploy to staging

**Outcome:** Developers internalize secure coding patterns through:
- Clear specifications (not tribal knowledge)
- Immediate feedback (CI/CD gates)
- Practical experience (writing secure code)

---

## 🔍 Specification Files Explained

### Security Specifications

| File | Purpose | Enforcement Level |
|------|---------|-------------------|
| `secrets_management.spec` | How to handle credentials | CRITICAL (blocking) |
| `sql_injection_prevention.spec` | Database query security | CRITICAL (blocking) |
| `web_security.spec` | OWASP Top 10 controls | CRITICAL (blocking) |
| `dependency_management.spec` | Supply chain security | REQUIRED |

### Architecture Specifications

| File | Purpose | Enforcement Level |
|------|---------|-------------------|
| `database_layer.spec` | DB connection patterns | REQUIRED |
| `web_application.spec` | Application structure | REQUIRED |

### Testing Specifications

| File | Purpose | Enforcement Level |
|------|---------|-------------------|
| `security_tests.spec` | Required security tests | CRITICAL (blocking) |

### Deployment Specifications

| File | Purpose | Enforcement Level |
|------|---------|-------------------|
| `dockerfile.spec` | Container security | CRITICAL (blocking) |
| `ci_cd_pipeline.spec` | Pipeline requirements | REQUIRED |

---

## ✅ What This Template Prevents

### ❌ Common Vulnerabilities Blocked

1. **Hardcoded Secrets**
   - Spec: `secrets_management.spec`
   - Gate: `detect-secrets` scan in CI/CD
   - Blocked: Deployment fails if secrets detected

2. **SQL Injection**
   - Spec: `sql_injection_prevention.spec`
   - Gate: Security tests + Bandit static analysis
   - Blocked: Tests fail if non-parameterized queries exist

3. **Missing CSRF Protection**
   - Spec: `web_security.spec`
   - Gate: Security tests verify CSRF enabled
   - Blocked: Tests fail if CSRF not configured

4. **Vulnerable Dependencies**
   - Spec: `dependency_management.spec`
   - Gate: `pip-audit` in CI/CD
   - Blocked: Build fails if HIGH/CRITICAL CVEs found

5. **Running as Root**
   - Spec: `dockerfile.spec`
   - Gate: Container scan + Kubernetes security context
   - Blocked: Deployment fails if running as root

6. **Unpinned Dependencies**
   - Spec: `dependency_management.spec`
   - Gate: CI/CD checks for `==` pinning
   - Blocked: Build fails if loose version constraints

---

## 📊 Success Metrics

Track these metrics to measure template effectiveness:

- **Security Gate Failures**: Should decrease over time (learning)
- **Time to First Secure Deployment**: Should decrease (efficiency)
- **Production Security Incidents**: Should be zero (prevention)
- **Dependency CVEs**: Detected before production (supply chain)
- **Code Review Findings**: Fewer security issues (quality)

---

## 🛠️ Customization

### Adding New Specifications

1. Create spec file in appropriate directory:
   ```
   skeleton/specs/security/new_security_control.spec
   ```

2. Follow specification template format:
   ```
   ================================================================================
   SPECIFICATION: [Name]
   Category: [Security|Architecture|Testing|Deployment]
   Enforcement Level: [CRITICAL|REQUIRED|RECOMMENDED]
   Version: 1.0
   ================================================================================

   PURPOSE
   -------
   [What this spec addresses]

   SCOPE
   -----
   [When this spec applies]

   ================================================================================
   MANDATORY REQUIREMENTS
   ================================================================================

   REQ-1: [Requirement name]
     Rule: [Clear statement]
     ✅ COMPLIANT: [Example]
     ❌ NON-COMPLIANT: [Counter-example]
   ```

3. Reference in `CLAUDE.md` and `docs/ENTERPRISE_STANDARDS.md`

4. Add validation to your CI/CD pipeline if enforceable

### Modifying for Different Frameworks

Currently Flask-focused. To adapt for Django/FastAPI:

1. Update `web_application.spec` with framework-specific patterns
2. Modify `web_security.spec` for framework's security features
3. Update `requirements.txt` with appropriate packages
4. Adjust `CLAUDE.md` examples

---

## 📞 Support & Contributing

### Questions?
- Template issues: File GitHub issue
- Security questions: #security-guild
- Backstage integration: #platform-engineering

### Contributing
1. Fork repository
2. Create feature branch
3. Add/modify specifications
4. Test with generated project
5. Submit pull request

---

## 📚 References

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **CWE Top 25**: https://cwe.mitre.org/top25/
- **NIST SSDF**: Secure Software Development Framework
- **Backstage**: https://backstage.io/docs/features/software-templates/

---

## 📄 License

[Add your license]

---

**Template Version:** 2.0  
**Last Updated:** 2026-06-10  
**Maintained By:** Platform Engineering Team

**Philosophy:** Secure by default, compliant by design, enforced by automation.
