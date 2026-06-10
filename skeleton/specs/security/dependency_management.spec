================================================================================
SPECIFICATION: Dependency Management & Supply Chain Security
Category: Security
Enforcement Level: REQUIRED
Version: 2.0
================================================================================

PURPOSE
-------
Ensure secure, vetted, and maintainable Python dependencies.

SCOPE
-----
All Python packages listed in requirements.txt

================================================================================
MANDATORY REQUIREMENTS
================================================================================

REQ-1: PIN ALL VERSIONS
  Rule: ALL dependencies MUST be pinned to specific versions using ==

  ✅ COMPLIANT:
    Flask==3.0.3
    psycopg2-binary==2.9.9
    gunicorn==22.0.0

  ❌ NON-COMPLIANT:
    Flask>=3.0  # Loose constraint
    psycopg2-binary  # No version
    gunicorn~=22.0  # Compatible release

  Why: Reproducible builds, prevent surprise breakage

REQ-2: VULNERABILITY SCANNING
  Rule: ALL dependencies MUST be scanned for known CVEs

  Tool: pip-audit or safety
  Frequency: Every build + weekly scheduled scan
  Action: Block deployment if HIGH/CRITICAL CVEs found

  Command:
    pip-audit -r requirements.txt

  Pass Criteria: Zero vulnerabilities of HIGH or CRITICAL severity

REQ-3: SBOM GENERATION
  Rule: Generate Software Bill of Materials for every deployment

  Tool: cyclonedx-bom
  Format: CycloneDX (JSON or XML)
  Command:
    cyclonedx-py requirements -r requirements.txt -o sbom.json

  Purpose:
    - Compliance tracking
    - Vulnerability management
    - License compliance
    - Supply chain transparency

REQ-4: APPROVED SOURCES
  Rule: Install packages only from approved sources

  Approved:
    - PyPI (https://pypi.org) - default
    - Internal artifact repository (preferred for production)

  Forbidden:
    - GitHub direct installs (except approved exceptions)
    - Unknown/unverified package indexes
    - Local file installs in production

REQ-5: REGULAR UPDATES
  Rule: Update dependencies monthly (security patches more frequently)

  Process:
    1. Check for updates: pip list --outdated
    2. Review changelogs for breaking changes
    3. Update requirements.txt
    4. Run full test suite
    5. Security scan updated dependencies
    6. Deploy to staging first
    7. Monitor for issues
    8. Deploy to production

  Critical Security Updates:
    - Apply within 7 days of disclosure
    - Emergency process for active exploits

================================================================================
DEPENDENCY CATEGORIES
================================================================================

PRODUCTION DEPENDENCIES (requirements.txt):
  - Required for application runtime
  - Included in production container
  - Fully vetted and scanned

DEVELOPMENT DEPENDENCIES (requirements-dev.txt):
  - Testing, linting, local development
  - NOT included in production container
  - Still scanned for vulnerabilities

EXAMPLE requirements.txt:
```
# Web Framework
Flask==3.0.3
Werkzeug==3.0.3

# Database
psycopg2-binary==2.9.9

# Security
Flask-WTF==1.2.1
WTForms==3.1.2
python-dotenv==1.0.1

# Production Server
gunicorn==22.0.0
```

EXAMPLE requirements-dev.txt:
```
# Testing
pytest==8.2.2
pytest-cov==5.0.0
pytest-mock==3.14.0

# Code Quality
black==24.4.2
flake8==7.0.0
mypy==1.10.0

# Security Scanning
pip-audit==2.7.3
bandit==1.7.8

# SBOM Generation
cyclonedx-bom==4.5.0
```

================================================================================
PACKAGE VETTING PROCESS
================================================================================

Before Adding New Dependency:

STEP 1: Necessity Check
  Question: Is this package truly needed?
  Consider:
    - Can we use standard library instead?
    - Is there an approved alternative?
    - What's the maintenance burden?

STEP 2: Security Review
  Check:
    - Known vulnerabilities (CVE database)
    - Security advisories on GitHub
    - pip-audit scan results

STEP 3: Maintenance Status
  Verify:
    - Last release date (< 1 year preferred)
    - Active maintainers
    - Issue response time
    - GitHub stars/forks (community health)

STEP 4: License Compliance
  Verify:
    - License compatible with company policy
    - No GPL/AGPL (if prohibited)
    - License clearly documented

STEP 5: Documentation Quality
  Check:
    - README exists
    - API documentation
    - Examples available
    - Changelog maintained

STEP 6: Testing
  Verify:
    - Package has test suite
    - CI/CD configured
    - Test coverage reasonable

STEP 7: Approval
  Process:
    - Document justification
    - Security team review (if sensitive)
    - Add to approved packages list
    - Pin specific version

================================================================================
BLOCKLIST (FORBIDDEN PACKAGES)
================================================================================

Packages with Known Issues:
  - Packages with unfixed CRITICAL CVEs
  - Packages abandoned >2 years
  - Packages with malware history

Common Problematic Packages:
  - Packages with unclear licensing
  - Packages with known backdoors
  - Packages with supply chain attacks

Process:
  - Maintain internal blocklist
  - Automated checking in CI/CD
  - Block installation attempts

================================================================================
DEPENDENCY VULNERABILITY MANAGEMENT
================================================================================

Severity Levels & Response Times:

CRITICAL (CVSS 9.0-10.0):
  - Response: Immediate (within 24 hours)
  - Action: Emergency patch or removal
  - Deployment: Expedited to production

HIGH (CVSS 7.0-8.9):
  - Response: Within 7 days
  - Action: Update or find alternative
  - Deployment: Next release cycle

MEDIUM (CVSS 4.0-6.9):
  - Response: Within 30 days
  - Action: Update in next sprint
  - Deployment: Regular release

LOW (CVSS 0.1-3.9):
  - Response: Within 90 days
  - Action: Update when convenient
  - Deployment: Regular maintenance

================================================================================
requirements.txt STRUCTURE
================================================================================

Recommended Format:

```
# ============================================================================
# PRODUCTION DEPENDENCIES
# Project: Application Name
# Python: 3.11+
# Last Updated: 2026-06-10
# ============================================================================

# Web Framework
Flask==3.0.3              # Web framework
Werkzeug==3.0.3           # WSGI utilities (Flask dependency)

# Database
psycopg2-binary==2.9.9    # PostgreSQL adapter (binary distribution)

# Security
Flask-WTF==1.2.1          # CSRF protection for Flask
WTForms==3.1.2            # Form validation
python-dotenv==1.0.1      # Environment variable loading

# Production Server
gunicorn==22.0.0          # WSGI HTTP server

# Utilities
[additional packages]

# ============================================================================
# SECURITY NOTES:
# - All versions pinned with ==
# - Scanned with pip-audit (last scan: 2026-06-10)
# - SBOM generated with cyclonedx-bom
# - Update monthly (next review: 2026-07-10)
# ============================================================================
```

Benefits:
  - Grouped by purpose
  - Documented versions
  - Clear update schedule
  - Audit trail

================================================================================
AUTOMATED DEPENDENCY UPDATES
================================================================================

Tools:
  - Dependabot (GitHub)
  - Renovate Bot
  - pyup.io

Configuration:
  - Weekly update checks
  - Automated PR creation
  - Automated security patches
  - Grouped updates by category

Review Process:
  1. Bot creates PR with version update
  2. Automated tests run
  3. Security scans execute
  4. Review changelog for breaking changes
  5. Manual approval
  6. Merge to staging
  7. Deploy and monitor
  8. Promote to production

================================================================================
MONITORING & ALERTS
================================================================================

Continuous Monitoring:
  - Daily CVE database checks
  - Weekly dependency update checks
  - Monthly license compliance scans

Alerts:
  - New CVE affecting dependencies
  - Dependency EOL announcements
  - License changes in dependencies
  - Supply chain attack indicators

Dashboard Metrics:
  - Total dependencies count
  - Outdated packages count
  - Known vulnerabilities count
  - Average dependency age
  - License distribution

================================================================================
TESTING WITH DEPENDENCIES
================================================================================

Before Updating:
  - Run full test suite
  - Security tests (especially for security packages)
  - Integration tests
  - Performance tests (check for regressions)

After Updating:
  - Verify application still works
  - Check for deprecation warnings
  - Monitor error rates in staging
  - Review logs for unusual behavior

================================================================================
DOCUMENTATION REQUIREMENTS
================================================================================

Required Documentation:
  - Why each dependency is needed
  - Update schedule
  - Known issues/workarounds
  - Version constraints rationale

Example (README.md):
```markdown
## Dependencies

### Web Framework
- **Flask 3.0.3**: Web application framework
- **Reason**: Team standard, security support, good documentation
- **Update Policy**: Monthly, test thoroughly before production

### Database
- **psycopg2-binary 2.9.9**: PostgreSQL adapter
- **Reason**: Stable, well-maintained, binary distribution for easy install
- **Note**: Using binary version (not psycopg2) for simpler deployment
```

================================================================================
VALIDATION CHECKLIST
================================================================================

Before committing requirements.txt:
[ ] All versions pinned with ==
[ ] All packages necessary
[ ] No known HIGH/CRITICAL CVEs
[ ] SBOM generated
[ ] Comments explain purpose of packages
[ ] Update schedule documented
[ ] Blocklist checked

Before production deployment:
[ ] pip-audit scan passed
[ ] All tests passed with new dependencies
[ ] Staging deployment successful
[ ] No unexpected behavior
[ ] Performance acceptable
[ ] Security review completed (if major update)

================================================================================
REFERENCES
================================================================================

- OWASP Dependency Check
- NIST NVD (National Vulnerability Database)
- PyPI Security Advisories
- CycloneDX SBOM Standard

================================================================================
END OF SPECIFICATION
================================================================================
