================================================================================
SPECIFICATION: CI/CD Pipeline Standards
Category: Deployment
Enforcement Level: REQUIRED
Version: 2.0
================================================================================

PURPOSE
-------
Define mandatory CI/CD pipeline stages with security gates.
This is a CI/CD-agnostic specification - implement with your platform of choice.

SCOPE
-----
All Python applications deploying to staging/production environments

SUPPORTED CI/CD PLATFORMS
--------------------------
- GitLab CI/CD (.gitlab-ci.yml)
- GitHub Actions (.github/workflows/)
- Tekton/OpenShift Pipelines (Pipeline CRDs)
- Jenkins (Jenkinsfile)
- Azure DevOps (azure-pipelines.yml)
- Any other CI/CD system

NOTE: This spec defines WHAT is required, not HOW to implement it.
      Implement these stages using your organization's CI/CD platform.

================================================================================
PIPELINE STAGES (MANDATORY)
================================================================================

STAGE 1: Security Scan (BLOCKING)
STAGE 2: Test (BLOCKING)
STAGE 3: Build (BLOCKING)
STAGE 4: Deploy (MANUAL APPROVAL)

Failure Behavior:
  - Stages 1-3: Block pipeline on failure
  - Stage 4: Requires manual approval
  - No stage skipping allowed

================================================================================
STAGE 1: SECURITY SCAN
================================================================================

Purpose: Detect security vulnerabilities before building

SUB-STAGE 1.1: Secret Detection
  Tool: detect-secrets or trufflehog
  Action: Scan all files for hardcoded secrets
  Command:
    detect-secrets scan --all-files --force-use-all-plugins > .secrets.baseline
  Exit Code: Non-zero if secrets detected
  Block: YES

SUB-STAGE 1.2: SBOM Generation
  Tool: cyclonedx-bom
  Action: Generate Software Bill of Materials
  Command:
    cyclonedx-py requirements -r requirements.txt -o sbom.json
  Artifact: sbom.json (archive for compliance)
  Block: NO (generate only)

SUB-STAGE 1.3: Dependency Vulnerability Scan
  Tool: pip-audit or safety
  Action: Check dependencies for known CVEs
  Command:
    pip-audit -r requirements.txt --desc --format json --output audit-report.json
  Pass Criteria: Zero HIGH or CRITICAL CVEs
  Block: YES

SUB-STAGE 1.4: Static Code Analysis
  Tool: Bandit (Python security linter)
  Action: Scan code for security issues
  Command:
    bandit -r src/ -f json -o bandit-report.json
  Check: SQL injection, hardcoded passwords, etc.
  Block: YES (HIGH/CRITICAL findings)

================================================================================
STAGE 2: TEST
================================================================================

Purpose: Verify functionality and security controls

SUB-STAGE 2.1: Unit Tests
  Tool: pytest
  Action: Run all unit tests
  Command:
    pytest tests/ -v --cov=src --cov-report=xml --cov-report=term
  Pass Criteria: All tests pass, coverage ≥ 80%
  Block: YES

SUB-STAGE 2.2: Security Tests
  Tool: pytest
  Action: Run security-focused tests
  Command:
    pytest tests/test_security.py -v
  Pass Criteria: 100% pass rate
  Block: YES

SUB-STAGE 2.3: Code Quality
  Tool: flake8, black, mypy
  Action: Lint, format check, type check
  Commands:
    flake8 src/
    black --check src/
    mypy src/
  Pass Criteria: No violations
  Block: RECOMMENDED (can be WARNING only)

================================================================================
STAGE 3: BUILD
================================================================================

Purpose: Build and scan container image

SUB-STAGE 3.1: Container Build
  Tool: Docker or Buildah
  Action: Build container image
  Command:
    docker build -t $IMAGE:$TAG .
  Tagging:
    - $CI_COMMIT_SHA (unique)
    - latest (if main branch)
  Block: YES (build failure)

SUB-STAGE 3.2: Container Scanning
  Tool: Trivy or Snyk
  Action: Scan image for vulnerabilities
  Command:
    trivy image --exit-code 1 --severity HIGH,CRITICAL $IMAGE:$TAG
  Pass Criteria: Zero HIGH/CRITICAL vulnerabilities
  Block: YES

SUB-STAGE 3.3: Image Push
  Tool: Docker push to registry
  Action: Push image to container registry
  Command:
    docker push $IMAGE:$TAG
  Only If: Stages 3.1 and 3.2 passed
  Block: YES (push failure)

================================================================================
STAGE 4: DEPLOY
================================================================================

Purpose: Deploy to target environment

SUB-STAGE 4.1: Deploy to Staging
  Trigger: Automatic after successful build (main branch)
  Environment: Staging
  Action: Update Kubernetes deployment
  Command:
    kubectl set image deployment/$APP $APP=$IMAGE:$TAG -n staging
    kubectl rollout status deployment/$APP -n staging
  Verification: Health check responds 200
  Rollback: Automatic on health check failure

SUB-STAGE 4.2: Deploy to Production
  Trigger: Manual approval on tagged releases
  Environment: Production
  Action: Update Kubernetes deployment
  Command:
    kubectl set image deployment/$APP $APP=$IMAGE:$TAG -n production
    kubectl rollout status deployment/$APP -n production
  Verification:
    - Health check responds 200
    - No error spike in logs
    - Metrics within normal range
  Rollback: Manual trigger if issues detected

================================================================================
PIPELINE VARIABLES
================================================================================

Required Variables:
  CI_COMMIT_SHA: Git commit hash (unique identifier)
  CI_PROJECT_NAME: Project name
  CI_REGISTRY: Container registry URL
  CI_REGISTRY_USER: Registry authentication
  CI_REGISTRY_PASSWORD: Registry authentication (from secrets)

Computed Variables:
  IMAGE: $CI_REGISTRY/$CI_PROJECT_PATH
  TAG: $CI_COMMIT_SHA

Environment-Specific:
  KUBE_CONFIG: Kubernetes configuration (staging/production)
  NAMESPACE: Kubernetes namespace

================================================================================
IMPLEMENTATION GUIDE (CI/CD Agnostic)
================================================================================

NOTE: This section provides the COMMANDS to run in each stage.
      Adapt the syntax to your CI/CD platform (GitLab CI, GitHub Actions, Tekton, etc.)

STAGE 1: SECURITY SCAN
----------------------
Container Image: registry.access.redhat.com/ubi9/python-311:latest

Job 1: Secret Detection (BLOCKING)
  Commands:
    pip install detect-secrets
    detect-secrets scan --all-files --force-use-all-plugins > .secrets.baseline
  Exit Code: Must be 0 (no secrets found)

Job 2: Dependency Scanning (BLOCKING)
  Commands:
    pip install pip-audit
    pip-audit -r requirements.txt --desc --format json --output audit-report.json
  Exit Code: Must be 0 (no HIGH/CRITICAL CVEs)
  Artifacts: audit-report.json

Job 3: SBOM Generation (REQUIRED)
  Commands:
    pip install cyclonedx-bom
    cyclonedx-py requirements -r requirements.txt -o sbom.json
  Artifacts: sbom.json

Job 4: Static Analysis (BLOCKING)
  Commands:
    pip install bandit
    bandit -r src/ -ll -f json -o bandit-report.json
  Exit Code: Must be 0 (no HIGH/CRITICAL findings)
  Artifacts: bandit-report.json

STAGE 2: TEST
-------------
Container Image: registry.access.redhat.com/ubi9/python-311:latest

Job 1: Unit Tests (BLOCKING)
  Setup:
    pip install -r requirements.txt
  Commands:
    pytest tests/ -v --cov=src --cov-report=xml --cov-report=term
  Exit Code: Must be 0 (all tests pass)
  Coverage: Minimum 80%
  Artifacts: coverage.xml

Job 2: Security Tests (BLOCKING)
  Setup:
    pip install -r requirements.txt
  Commands:
    pytest tests/test_security.py -v
  Exit Code: Must be 0 (all security tests pass)
  Coverage: 100% of security-critical code

STAGE 3: BUILD
--------------
Job 1: Container Build
  Commands:
    podman build -t <IMAGE_NAME>:<TAG> .
    podman push <IMAGE_NAME>:<TAG>
  Exit Code: Must be 0 (build succeeds)

Job 2: Container Scanning (BLOCKING)
  Commands:
    trivy image --exit-code 1 --severity HIGH,CRITICAL <IMAGE_NAME>:<TAG>
  Exit Code: Must be 0 (no HIGH/CRITICAL CVEs)

STAGE 4: DEPLOY
---------------
Job 1: Deploy to Staging (MANUAL APPROVAL)
  Trigger: After successful build on main branch
  Commands:
    kubectl set image deployment/<APP_NAME> <APP_NAME>=<IMAGE>:<TAG> -n staging
    kubectl rollout status deployment/<APP_NAME> -n staging
  Approval: Optional

Job 2: Deploy to Production (MANUAL APPROVAL)
  Trigger: After successful build on tagged release
  Commands:
    kubectl set image deployment/<APP_NAME> <APP_NAME>=<IMAGE>:<TAG> -n production
    kubectl rollout status deployment/<APP_NAME> -n production
  Approval: REQUIRED (ops team)

================================================================================
PLATFORM-SPECIFIC EXAMPLES
================================================================================

For reference implementations, see:
  - GitLab CI: Create .gitlab-ci.yml using commands above
  - GitHub Actions: Create .github/workflows/ci.yml using commands above
  - Tekton: Create Pipeline CRD with tasks for each stage
  - Jenkins: Create Jenkinsfile with stages as defined above

Example file structures are available but not included in this template.
Implement using your organization's CI/CD platform and standards.

================================================================================
ARTIFACT MANAGEMENT
================================================================================

Artifacts to Archive:
  - SBOM (sbom.json)
  - Vulnerability scan reports (audit-report.json, trivy-report.json)
  - Test coverage reports (coverage.xml)
  - Security test results
  - Build logs

Retention:
  - Production deployments: 1 year
  - Development branches: 30 days
  - Test artifacts: 90 days

================================================================================
NOTIFICATIONS
================================================================================

Notify On:
  - Pipeline failure (any blocking stage)
  - Security scan findings (HIGH/CRITICAL)
  - Deployment to production (success/failure)
  - Test coverage drop below threshold

Notification Channels:
  - Slack/Teams (automated)
  - Email (deployment approvals)
  - PagerDuty (production failures)

================================================================================
ROLLBACK PROCEDURES
================================================================================

Automatic Rollback Triggers:
  - Health check failures after deployment
  - Error rate spike > 5%
  - Response time > 3x baseline

Manual Rollback:
  Command:
    kubectl rollout undo deployment/$APP -n production

  Verification:
    kubectl rollout status deployment/$APP -n production

================================================================================
COMPLIANCE & AUDIT
================================================================================

Required Records:
  - SBOM for every production deployment
  - Security scan results (all stages)
  - Deployment approval audit trail
  - Rollback events and reasons

Compliance Reports:
  - Weekly: Failed security scans
  - Monthly: Vulnerability trends
  - Quarterly: Deployment metrics

Access Control:
  - Developers: Can trigger pipelines
  - Security team: Can view all scan results
  - Ops team: Can approve production deployments
  - Audit: Read-only access to all artifacts

================================================================================
VALIDATION CHECKLIST
================================================================================

Before enabling pipeline:
[ ] All four stages defined
[ ] Security scans configured (blocking)
[ ] Security tests implemented
[ ] Container scanning enabled
[ ] Manual approval for production
[ ] Rollback procedures documented
[ ] Notifications configured
[ ] Artifact retention configured

Before production deployment:
[ ] All pipeline stages passed
[ ] Security scans: 0 HIGH/CRITICAL
[ ] Test coverage ≥ 80%
[ ] Container scan passed
[ ] SBOM generated
[ ] Deployment approved
[ ] Rollback plan ready

================================================================================
REFERENCES
================================================================================

- GitLab CI/CD Documentation
- Kubernetes Deployment Best Practices
- NIST Secure Software Development Framework
- OWASP DevSecOps Guidelines

================================================================================
END OF SPECIFICATION
================================================================================
