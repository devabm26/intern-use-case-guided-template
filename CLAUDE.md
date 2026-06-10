# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Type: Backstage Scaffolder Template

This is **NOT** a Python application. This is a **Backstage scaffolder template** that generates secure Python web applications. The actual application code lives in the `skeleton/` directory and gets templated when users scaffold new projects.

## Architecture Overview

### Template Structure
```
intern-use-case-guided-template/
├── template.yaml              # Backstage scaffolder definition
├── skeleton/                  # Template that gets scaffolded into new projects
│   ├── specs/                # Security & architecture specifications (.spec files)
│   ├── docs/                 # Generated project documentation
│   ├── CLAUDE.md            # AI development rules (for generated projects)
│   ├── Dockerfile           # Red Hat UBI-based container template
│   └── requirements.txt     # Python dependency template
├── README.md                 # Template documentation (this repo)
└── COMPLIANCE_MECHANISMS.md  # How security enforcement works
```

### Key Concept: Specifications Over Boilerplate

This template uses **specification files** (`.spec`) instead of pre-written code:
- **Traditional templates**: Ship boilerplate code that can be modified insecurely
- **This template**: Ships specifications that define WHAT to build and HOW to build it securely

Example: Instead of shipping `database.py` with connection code, we ship `specs/architecture/database_layer.spec` that defines the approved patterns for database connections.

## Working with This Repository

### Template Development Commands

**Install Backstage dependencies** (if testing locally):
```bash
# This template is designed to be used with Backstage
# Local testing would require a Backstage instance
```

**Validate template.yaml**:
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('template.yaml'))"
```

**Test template scaffolding** (manual):
```bash
# Copy skeleton to test location
cp -r skeleton/ /tmp/test-project/
cd /tmp/test-project/

# Manually replace template variables to simulate scaffolding
# ${{ values.component_id }} → test-app
# ${{ values.owner }} → test-team
# etc.
```

### File Modification Guidelines

**When editing specifications** (`skeleton/specs/**/*.spec`):
1. Follow the specification template format (see existing .spec files)
2. Include both ✅ APPROVED and ❌ FORBIDDEN patterns with examples
3. Update `skeleton/CLAUDE.md` if adding new security requirements
4. Update `skeleton/docs/ENTERPRISE_STANDARDS.md` if changing compliance requirements

**When editing skeleton/CLAUDE.md**:
- This file guides AI assistants working in **generated projects** (not this repo)
- Changes affect all future scaffolded applications
- Keep security rules as ABSOLUTE RULES (non-negotiable)
- Include clear examples of compliant vs non-compliant code

**When editing template.yaml**:
- This defines the Backstage scaffolder parameters and steps
- Test that all parameter validations make sense
- Ensure template variables match what's used in skeleton files

**When editing skeleton/Dockerfile**:
- **MUST** use Red Hat UBI base images only
- **MUST** maintain non-root user (UID 1001)
- Multi-stage builds required (builder + runtime)
- Document why each step exists

## Critical Template Design Principles

### 1. Security by Default
Generated projects must be secure even if developers don't read documentation:
- Environment variables for secrets (never hardcoded)
- Parameterized SQL queries (prevent injection)
- Red Hat UBI containers (non-root by default)
- CI/CD gates (block insecure deployments)

### 2. AI-Friendly Documentation
Files in `skeleton/` are read by AI coding assistants:
- **skeleton/CLAUDE.md**: Rules for AI-assisted development
- **skeleton/.claude/project-instructions.md**: Auto-loaded by Claude Code
- **skeleton/specs/**: Machine-readable security specifications

### 3. Enforcement Layers
Three layers prevent insecure code from reaching production:
1. **Preventive**: Specifications guide implementation
2. **Detective**: Security tests catch violations
3. **Blocking**: CI/CD gates prevent deployment

## Repository-Specific Considerations

### Red Hat UBI Containers
This template exclusively uses Red Hat Universal Base Images:
- `registry.access.redhat.com/ubi9/python-311:latest`
- Free to use and redistribute
- Enterprise-grade security patches
- Already runs as non-root (UID 1001)
- No authentication required to pull

**Never suggest**: Alpine, Debian, Ubuntu, or generic Python base images.

### Specification File Format
When creating or modifying `.spec` files:
```
================================================================================
SPECIFICATION: [Name]
Category: [Security|Architecture|Testing|Deployment]
Enforcement Level: [CRITICAL|REQUIRED|RECOMMENDED]
Version: [X.Y]
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
  
  ✅ COMPLIANT:
    [Code example that follows the rule]
  
  ❌ NON-COMPLIANT:
    [Code example that violates the rule]
    Reason: [Why this is insecure/wrong]

[Additional requirements...]
```

### Template Variable Naming
Backstage template variables use this format: `${{ values.parameter_name }}`

Common variables defined in template.yaml:
- `${{ values.component_id }}` - Application name
- `${{ values.owner }}` - Team/user owner
- `${{ values.description }}` - Project description
- `${{ values.db_host }}` - Database hostname
- `${{ values.db_name }}` - Database name

## Common Tasks

### Adding a New Security Specification

1. Create spec file:
   ```bash
   # Example: Adding API authentication spec
   touch skeleton/specs/security/api_authentication.spec
   ```

2. Write specification following template format (see above)

3. Reference in skeleton/CLAUDE.md:
   ```markdown
   ## API Authentication
   **ABSOLUTE RULE: All API endpoints MUST require authentication.**
   
   See: specs/security/api_authentication.spec
   ```

4. Update skeleton/docs/ENTERPRISE_STANDARDS.md with the new requirement

5. Add validation to skeleton/specs/deployment/ci_cd_pipeline.spec if enforceable

### Updating Base Container Image

When Red Hat releases new UBI versions:

1. Update skeleton/Dockerfile:
   ```dockerfile
   FROM registry.access.redhat.com/ubi9/python-311:YYYYMMDD-VERSION
   ```

2. Test build:
   ```bash
   cd skeleton/
   docker build -t test:latest .
   ```

3. Scan for vulnerabilities:
   ```bash
   trivy image --severity HIGH,CRITICAL test:latest
   ```

4. Update skeleton/README.md with new image version

### Testing Template Changes

Since this is a Backstage template, testing requires either:

**Option 1: Manual scaffolding test**
```bash
# Create test instance
cp -r skeleton/ /tmp/test-scaffolded-app/
cd /tmp/test-scaffolded-app/

# Replace template variables manually
find . -type f -exec sed -i 's/\${{ values.component_id }}/test-app/g' {} \;
find . -type f -exec sed -i 's/\${{ values.owner }}/test-team/g' {} \;
# ... etc for all variables

# Verify it builds
docker build -t test-app:latest .
```

**Option 2: Backstage integration test**
- Requires access to a Backstage instance
- Create test component using this template
- Verify generated project structure

## Documentation Files

### Root-level Documentation (This Repository)
- **README.md**: Template overview, usage instructions, security mechanisms
- **COMPLIANCE_MECHANISMS.md**: How security is enforced (AI tools, tests, CI/CD)
- **DEVSPACES-VERTEX-AI-SETUP.md**: Using template in OpenShift Dev Spaces

### Skeleton Documentation (Generated Projects)
- **skeleton/README.md**: Generated project README (scaffolded with variables replaced)
- **skeleton/CLAUDE.md**: AI development rules for generated projects
- **skeleton/docs/ENTERPRISE_STANDARDS.md**: Authoritative security standards
- **skeleton/docs/PROMPTING_GUIDE.md**: How to prompt AI tools to follow specs

## Integration Points

### Backstage
- Template defined in `template.yaml`
- Scaffolder parameters define user inputs
- `fetch:template` action processes skeleton directory
- `publish:gitlab` creates repository
- `catalog:register` adds to Backstage catalog

### GitLab/GitHub
- Generated projects include `.gitignore`
- CI/CD configuration NOT included (platform-specific)
- Specifications define what CI/CD must implement
- See `skeleton/specs/deployment/ci_cd_pipeline.spec`

### Red Hat OpenShift Dev Spaces
- `.devcontainer/` directory for Dev Spaces support
- `.devfile.yaml` for workspace configuration
- `.devspaces/load-context.sh` for Vertex AI Claude integration
- See DEVSPACES-VERTEX-AI-SETUP.md

## What NOT to Do

### Don't Add Pre-Written Application Code
This template provides specifications, not implementations:
- ❌ Don't create `skeleton/src/app.py` with Flask app code
- ✅ Do create `skeleton/specs/architecture/web_application.spec` with patterns

### Don't Use Non-Red Hat Base Images
For enterprise compliance:
- ❌ Don't use `python:3.11-slim`, `python:alpine`, `ubuntu:latest`
- ✅ Do use `registry.access.redhat.com/ubi9/python-311:latest`

### Don't Make Security Optional
All security controls are mandatory:
- ❌ Don't add flags like `--skip-security` or `enable_security: false`
- ✅ Do enforce through specifications + tests + CI/CD gates

### Don't Bypass Specification System
The spec-driven approach is the key innovation:
- ❌ Don't add boilerplate code that can be modified insecurely
- ✅ Do add specifications that define secure patterns

## Success Criteria

Changes to this template are successful when:
- Generated projects pass all security scans
- AI assistants can read specifications and implement securely
- CI/CD gates block insecure code from deployment
- Developers receive clear error messages when violations occur
- Template remains platform-agnostic (works with any CI/CD)

## Support Resources

- **Backstage Documentation**: https://backstage.io/docs/features/software-templates/
- **Red Hat UBI Images**: https://catalog.redhat.com/software/containers/explore
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **NIST SSDF**: Secure Software Development Framework

---

**Remember**: This is a template for generating projects, not a project itself. Changes here affect all future scaffolded applications. Test thoroughly before deploying template updates.
