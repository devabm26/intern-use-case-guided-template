================================================================================
SPECIFICATION: Container Security - Dockerfile Standards
Category: Deployment
Enforcement Level: CRITICAL (BLOCKING)
Version: 2.0
================================================================================

PLATFORM ENFORCEMENT NOTICE
----------------------------
This specification is enforced by the Application Platform through:

✅ Backstage Templates: Auto-generate compliant Containerfiles
✅ CI/CD Pipelines: Block builds that violate security standards
✅ Container Scanning: Trivy/RHACS scans block deployment on HIGH/CRITICAL CVEs
✅ TPA Integration: Real-time package vulnerability checking
✅ Automated Reviews: Platform validates compliance before merge

WITHOUT PLATFORM: These are guidelines developers might ignore or forget
WITH PLATFORM: These are enforced guardrails that prevent insecure deployments

Platform Benefit: Developers get secure-by-default templates instead of writing
                  Dockerfiles from scratch. Security is built-in, not bolted-on.

================================================================================

PURPOSE
-------
Ensure all container images follow security best practices.

SCOPE
-----
All Dockerfile definitions for Python applications

================================================================================
APPROVED BASE IMAGES
================================================================================

IMAGE SELECTION STRATEGY:
  🥇 PREFERRED: Hardened images for runtime (maximum security)
  🥈 ALTERNATIVE: UBI images when debugging/package management needed
  🏗️  BUILDER STAGE: Always use UBI (requires package manager)

HARDENED IMAGES (Red Hat Hardened - PREFERRED FOR RUNTIME):
  registry.access.redhat.com/hi/python:latest

CHARACTERISTICS:
  - Distroless-style minimal image
  - NO package manager (no dnf, yum, apt)
  - NO shell (/bin/sh not available)
  - Runs as non-root UID 65532 (hardcoded)
  - Minimal attack surface (smallest possible image)
  - Contains only Python runtime and essential libraries
  - Red Hat security updates and support

WHY HARDENED IMAGES ARE PREFERRED:
  ✅ Maximum security - minimal attack surface
  ✅ No package manager - eliminates entire class of vulnerabilities
  ✅ No shell - prevents shell injection attacks
  ✅ Smallest image size - faster deployments
  ✅ Immutable runtime - no modification possible
  ✅ Compliance ready - meets strictest security standards
  ✅ Production-optimized - designed for runtime only

WHEN TO USE HARDENED IMAGES:
  ✅ ALL production runtime workloads (default choice)
  ✅ Security-sensitive applications
  ✅ Compliance-required environments (PCI-DSS, HIPAA, etc.)
  ✅ Applications with all dependencies pre-built
  ✅ Stateless microservices

LIMITATIONS & CONSIDERATIONS:
  ⚠️  Cannot install packages at runtime (no package manager)
  ⚠️  Cannot use dnf/yum commands in Dockerfile RUN steps
  ⚠️  All dependencies MUST be installed in builder stage
  ⚠️  Debugging requires using ephemeral debug containers
  ⚠️  Fixed UID 65532 (cannot change user)
  ⚠️  No shell - cannot use RUN commands with shell syntax

USAGE PATTERN (Multi-stage build REQUIRED):
  # Stage 1: Builder (use UBI with package manager)
  FROM registry.access.redhat.com/ubi9/python-311:latest AS builder
  RUN dnf install -y gcc postgresql-devel && dnf clean all
  # ... build dependencies and virtual environment ...

  # Stage 2: Runtime (PREFERRED - hardened image)
  FROM registry.access.redhat.com/hi/python:latest
  # No RUN commands with package installation
  COPY --from=builder /opt/venv /opt/venv
  # Image already runs as UID 65532 - no USER directive needed
  CMD ["gunicorn", "app:app"]

UNIVERSAL BASE IMAGES (Red Hat UBI - Use for Builder or when hardened not suitable):
  registry.access.redhat.com/ubi9/python-311:latest
  registry.access.redhat.com/ubi9/python-39:latest
  registry.access.redhat.com/ubi8/python-39:latest

REQUIREMENTS:
  - Red Hat UBI (Universal Base Image) - enterprise-grade
  - RHEL-based (security patches from Red Hat)
  - Free to use and redistribute
  - Active Red Hat security support
  - Already runs as non-root (UID 1001)

WHY RED HAT UBI:
  - Enterprise support and SLA
  - Security updates from Red Hat
  - Compliance and certification (FIPS, Common Criteria)
  - Consistent with Red Hat OpenShift environments
  - Built-in security best practices
  - Package manager available (dnf/yum)
  - Shell available for debugging

WHEN TO USE UBI (instead of hardened):
  ✅ Builder stage (ALWAYS - requires package manager)
  ✅ Development/testing environments (easier debugging)
  ✅ When runtime package installation is required
  ✅ Legacy applications not compatible with distroless
  ✅ Troubleshooting production issues (temporary)

DECISION TREE - WHICH IMAGE TO USE:

  Is this a builder stage?
    YES → Use UBI (registry.access.redhat.com/ubi9/python-311:latest)

  Is this a runtime stage for production?
    YES → Do you need to install packages at runtime?
      NO  → ✅ Use HARDENED (registry.access.redhat.com/hi/python:latest)
      YES → Use UBI (registry.access.redhat.com/ubi9/python-311:latest)

  Is this for development/debugging?
    YES → Use UBI (registry.access.redhat.com/ubi9/python-311:latest)

FORBIDDEN:
  ❌ python:latest (unpredictable, breaks reproducibility)
  ❌ python:3.8 or older (EOL, no security patches)
  ❌ python:alpine (compatibility issues with psycopg2, numpy, etc.)
  ❌ ubuntu, debian base images (use Red Hat UBI for enterprise)
  ❌ Custom base images (without security approval)
  ❌ Non-Red Hat images in Red Hat OpenShift environments

================================================================================
PYTHON DEPENDENCY MANAGEMENT
================================================================================

REQUIREMENTS FILES STRUCTURE (MANDATORY):

  requirements.txt (Runtime dependencies ONLY):
    - Production dependencies needed to run the application
    - Installed in the runtime container
    - Keep minimal - fewer packages = smaller attack surface
    - Pin all versions with == (no >=, no ~=)

    Example:
      Flask==3.0.3
      psycopg2-binary==2.9.9
      gunicorn==22.0.0
      python-dotenv==1.0.1

  requirements-dev.txt (Development/Security tooling ONLY):
    - Security scanning tools (pip-audit, bandit, detect-secrets)
    - Testing frameworks (pytest, pytest-cov)
    - Linting tools (flake8, black, mypy)
    - Development utilities
    - NEVER installed in runtime container
    - Used only in CI/CD pipelines and local development

    Example:
      pip-audit==2.7.3
      bandit==1.7.9
      detect-secrets==1.4.0
      pytest==8.2.2
      pytest-cov==5.0.0
      flake8==7.0.0

WHY SEPARATION MATTERS:
  ✅ Smaller runtime image (fewer packages)
  ✅ Reduced attack surface (fewer dependencies = fewer CVEs)
  ✅ Faster container startup (less to load)
  ✅ Clear separation of concerns
  ✅ Security tooling runs in CI/CD, not production
  ✅ Fair vulnerability comparison (apples-to-apples)

CONTAINERFILE PATTERN:
  # Builder stage - install runtime dependencies only
  COPY requirements.txt .
  RUN pip install --no-cache-dir --upgrade pip && \
      pip install --no-cache-dir -r requirements.txt

  # Security scanning happens in CI/CD (NOT in Containerfile):
  # pip install -r requirements-dev.txt
  # pip-audit --require-hashes
  # bandit -r src/
  # detect-secrets scan

VERSION PINNING RULE:
  - ALL packages MUST use == (exact version)
  - NEVER use >= (unpredictable, allows drift)
  - NEVER use ~= (allows patch version drift)
  - NEVER leave unpinned (reproducibility failure)

  Bad:
    Flask>=3.0        # Allows 3.1, 3.2, etc.
    psycopg2-binary   # Unpinned - could install any version

  Good:
    Flask==3.0.3      # Exact version, immutable
    psycopg2-binary==2.9.9

FORBIDDEN IN requirements.txt:
  ❌ Development tools (pytest, flake8, black)
  ❌ Security scanners (pip-audit, bandit, detect-secrets)
  ❌ Build tools (setuptools, wheel) - use build backend only
  ❌ Unpinned versions (>=, ~=, or no version)

================================================================================
MANDATORY DOCKERFILE PATTERNS
================================================================================

REQ-1: MULTI-STAGE BUILDS (REQUIRED)
  Purpose: Minimize final image size, separate build and runtime

  Structure:
    Stage 1: Builder (UBI with package manager)
      - Switch to root (for dnf install)
      - Install build dependencies (gcc, postgresql-devel, python3-devel)
      - Build Python packages
      - Create virtual environment
      - Clean dnf cache

    Stage 2: Runtime (Hardened or UBI)
      - Copy only virtual environment from builder
      - Copy application code
      - Run as non-root user (65532 for hardened, 1001 for UBI)

  Builder Stage Pattern:
    FROM registry.access.redhat.com/ubi9/python-39:latest AS builder

    # UBI images default to non-root - switch to root for system packages
    USER root

    # Install build dependencies
    RUN dnf install -y \
            gcc \
            postgresql-devel \
            python3-devel \
        && dnf clean all \
        && rm -rf /var/cache/dnf

    # Create and use virtual environment
    RUN python -m venv /opt/venv
    ENV PATH="/opt/venv/bin:$PATH"

    COPY requirements.txt .
    RUN pip install --no-cache-dir --upgrade pip && \
        pip install --no-cache-dir -r requirements.txt

  Why python3-devel is required:
    - Needed to compile Python packages with C extensions
    - Required for packages like psycopg2, numpy, pandas
    - Must be installed in builder (not available in hardened image)

  Why USER root in builder:
    - UBI images default to UID 1001 (non-root)
    - dnf requires root privileges
    - Builder is discarded (never shipped), so root is safe here
    - Final runtime image still runs as non-root

REQ-2: NON-ROOT USER
  Rule: Container MUST run as non-root user (UID 1000+)

  Pattern (Hardened Image):
    # Hardened image runs as UID 65532 by default
    # Explicitly set for clarity (best practice)
    USER 65532

  Pattern (Red Hat UBI):
    # Red Hat UBI images run as UID 1001 by default
    # Explicitly set for clarity
    USER 1001

  Pattern (Generic images - create user):
    # Create user
    RUN groupadd -r appuser && \
        useradd -r -g appuser -u 1000 appuser

    # Switch to non-root
    USER appuser

  Why: Prevents privilege escalation attacks

  File Ownership:
    - Hardened image: Use --chown=65532:0 when copying files
    - UBI image: Use --chown=1001:0 when copying files
    - Group 0 (root group) is required for OpenShift compatibility

REQ-3: NO SECRETS IN LAYERS
  Rule: NO secrets, credentials, keys in any image layer

  Forbidden:
    ❌ ENV DB_PASSWORD=hardcoded
    ❌ COPY credentials.json /app/
    ❌ RUN echo "secret" > /app/config

  Approved: Runtime injection via Kubernetes Secrets

REQ-4: MINIMAL INSTALLED PACKAGES
  Rule: Install only required packages, remove build dependencies

  Pattern (Red Hat UBI - using dnf):
    # Install runtime dependencies
    RUN dnf install -y \
        postgresql \
        && dnf clean all

  Pattern (Debian-based - using apt):
    # Install runtime dependencies
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
        libpq5 \
        && rm -rf /var/lib/apt/lists/*

  Avoid: Build tools (gcc, make) in final image

REQ-5: HEALTH CHECK
  Rule: Define HEALTHCHECK instruction

  Pattern (works in both UBI and hardened images):
    HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
        CMD python -c \
            "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" \
            || exit 1

  Why this works in hardened images:
    - Uses Python stdlib (urllib) - no external tools required
    - No shell commands (curl, wget) needed
    - Pure Python execution
    - exit 1 on failure for proper signal

  Alternative (Kubernetes probes - also valid):
    livenessProbe:
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 30

REQ-6: EXPLICIT PORTS
  Rule: EXPOSE ports used by application

  Pattern:
    EXPOSE 8080

  Note: Use port 8080 (not privileged ports like 80) for non-root containers

REQ-7: PRODUCTION SERVER
  Rule: Use production WSGI/ASGI server (NOT Flask dev server)

  Approved:
    - Gunicorn (Flask, Django)
    - Uvicorn (FastAPI, async)
    - uWSGI (Django)

  Pattern (Gunicorn with container logging):
    CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", \
         "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", \
         "src.app:app"]

  Why use these flags:
    - --access-logfile "-" : Logs to stdout (container best practice)
    - --error-logfile "-"  : Errors to stderr (container best practice)
    - Enables log aggregation (12-factor app)
    - Works with kubectl logs, OpenShift logging

  Forbidden:
    ❌ flask run (development only)
    ❌ python app.py (development only)
    ❌ Gunicorn without logging flags (logs lost)

================================================================================
CONTAINERFILE HEADER DOCUMENTATION (REQUIRED)
================================================================================

Every Containerfile MUST include a header comment block documenting:
  - Application name
  - Runtime image and its characteristics
  - Builder image and its purpose
  - Reference to this spec

REQUIRED HEADER PATTERN:

# ================================================================================
# <Application Name> — Containerfile
# Runtime: registry.access.redhat.com/hi/python:latest (Hummingbird hardened,
#          Python 3.14, non-root UID 65532, no package manager — distroless-style)
# Builder: registry.access.redhat.com/ubi9/python-39:latest (has dnf to compile
#          native extensions; discarded after build — never ships in final image)
# Spec: specs/deployment/dockerfile.spec
# ================================================================================

WHY THIS MATTERS:
  - Documents image choice (why hardened vs UBI)
  - Explains security model (UID 65532, distroless)
  - Clarifies what's in runtime vs builder
  - Links to authoritative spec
  - Helps reviewers understand security posture
  - Self-documenting infrastructure

STAGE SEPARATOR COMMENTS (RECOMMENDED):

# ── Stage 1: Builder (UBI9 — has dnf, gcc, postgresql-devel) ─────────────────
# The builder is never shipped. It exists only to compile native extensions and
# install all Python packages into /opt/venv, which is then copied to runtime.

# ── Stage 2: Runtime (Hardened Image — no package manager, UID 65532) ─────────

BENEFITS:
  - Clear visual separation of stages
  - Explains purpose of each stage
  - Makes Containerfile easier to understand
  - Prevents accidental runtime package installation

================================================================================
RECOMMENDED CONTAINERFILE TEMPLATE (Hardened Runtime - PRODUCTION DEFAULT)
================================================================================

# ================================================================================
# <Application Name> — Containerfile
# Runtime: registry.access.redhat.com/hi/python:latest (Hummingbird hardened,
#          Python 3.14, non-root UID 65532, no package manager — distroless-style)
# Builder: registry.access.redhat.com/ubi9/python-39:latest (has dnf to compile
#          native extensions; discarded after build — never ships in final image)
# Spec: specs/deployment/dockerfile.spec
# ================================================================================

# ── Stage 1: Builder (UBI9 — has dnf, gcc, postgresql-devel) ─────────────────
# The builder is never shipped. It exists only to compile native extensions and
# install all Python packages into /opt/venv, which is then copied to runtime.
FROM registry.access.redhat.com/ubi9/python-39:latest AS builder

# Switch to root to install system packages (UBI images default to non-root)
USER root

# Install build dependencies — these are NOT in the final image
RUN dnf install -y \
        gcc \
        postgresql-devel \
        python3-devel \
    && dnf clean all \
    && rm -rf /var/cache/dnf

# Create virtual environment at /opt/venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies into the virtual environment
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime (Hardened Image — no package manager, UID 65532) ─────────
FROM registry.access.redhat.com/hi/python:latest

# Python runtime settings — NO secrets (injected at runtime via Kubernetes Secrets)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8080

# Copy only the pre-built venv — compiler and build tools stay in the builder
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

# Hardened image runs as UID 65532; use that for file ownership
COPY --chown=65532:0 src/    /app/src/
COPY --chown=65532:0 config/ /app/config/

# Explicitly set the hardened image's non-root user (best practice for clarity)
USER 65532

EXPOSE 8080

# Health check — uses Python stdlib only (no curl/wget in distroless image)
# This WORKS in hardened images when using Python's urllib (no shell required)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c \
        "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" \
        || exit 1

# Production WSGI server — flask dev server is forbidden (spec REQ-7)
# Include logging flags for container stdout/stderr (12-factor app)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", \
     "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", \
     "src.app:app"]

================================================================================
ALTERNATIVE DOCKERFILE TEMPLATE (Red Hat UBI - When hardened not suitable)
================================================================================

USE THIS TEMPLATE WHEN:
  - You need to install runtime packages (rare in production)
  - Debugging is needed (development/testing)
  - Legacy application compatibility issues with distroless

# Stage 1: Builder
FROM registry.access.redhat.com/ubi9/python-311:latest AS builder

# Install build dependencies (using dnf for RHEL)
RUN dnf install -y \
    gcc \
    postgresql-devel \
    && dnf clean all

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM registry.access.redhat.com/ubi9/python-311:latest

# Install runtime dependencies only (using dnf for RHEL)
RUN dnf install -y \
    postgresql \
    && dnf clean all

# Note: Red Hat UBI Python images already run as non-root user (UID 1001)
# This is a built-in security feature - no need to create user

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code (UBI default user is UID 1001, group 0)
COPY --chown=1001:0 src/ /app/src/
COPY --chown=1001:0 config/ /app/config/

# UBI images already run as non-root, explicitly set for clarity
USER 1001

# Expose port
EXPOSE 8000

# Health check (works with UBI since shell is available)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run with production server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60", "src.app:app"]

================================================================================
HARDENED IMAGE OPERATIONAL GUIDE
================================================================================

DEBUGGING HARDENED IMAGES:
  Since there's no shell, you cannot exec into the container.

  For debugging, use Kubernetes ephemeral debug containers:

    # Attach debug container with tools
    kubectl debug -it <pod-name> --image=registry.access.redhat.com/ubi9/ubi-minimal \
      --target=<container-name>

  Or temporarily switch to UBI image for troubleshooting:

    FROM registry.access.redhat.com/ubi9/python-311:latest  # instead of hi/python

KUBERNETES PROBES FOR HARDENED IMAGES:
  Do NOT use HEALTHCHECK instruction (requires shell).
  Use Kubernetes native probes instead:

  livenessProbe:
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 10
    periodSeconds: 30

  readinessProbe:
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 5
    periodSeconds: 10

================================================================================
BUILD ARGUMENTS & ENVIRONMENT VARIABLES
================================================================================

BUILD ARGUMENTS (ARG):
  Use for build-time configuration only
  Example:
    ARG PYTHON_VERSION=3.11
    FROM python:${PYTHON_VERSION}-slim-bookworm

ENVIRONMENT VARIABLES (ENV):
  Avoid for secrets (use runtime injection)
  Acceptable uses:
    - PATH modifications
    - Python settings (PYTHONUNBUFFERED=1)
    - Non-sensitive defaults

  Example:
    ENV PYTHONUNBUFFERED=1 \
        PYTHONDONTWRITEBYTECODE=1 \
        PATH="/opt/venv/bin:$PATH"

SECRETS INJECTION:
  Method: Kubernetes Secrets as environment variables
  NOT in Dockerfile: ENV SECRET_KEY=...

================================================================================
OPTIMIZATION BEST PRACTICES
================================================================================

LAYER CACHING:
  - Copy requirements.txt first (before app code)
  - Leverage Docker layer caching
  - Rebuild only when dependencies change

REDUCE IMAGE SIZE:
  - Use slim base images
  - Remove build dependencies in final stage
  - Clean apt cache: rm -rf /var/lib/apt/lists/*
  - Use .dockerignore (exclude tests, docs, .git)

SECURITY:
  - Scan with Trivy, Snyk, or similar
  - Update base images regularly
  - Pin dependency versions
  - Run as non-root

REPRODUCIBILITY:
  - Pin base image version
  - Pin all Python packages (requirements.txt)
  - Document build date/version

================================================================================
.dockerignore FILE (REQUIRED)
================================================================================

Purpose: Exclude unnecessary files from build context

Recommended .dockerignore:

.git
.gitignore
.env
.env.local
*.md
README.md
docs/
tests/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
htmlcov/
.vscode/
.idea/
*.log

Benefits:
  - Faster builds (smaller context)
  - No secrets accidentally copied
  - Smaller final image

================================================================================
SECURITY SCANNING REQUIREMENTS
================================================================================

TOOL: Trivy (or equivalent)

Scan Command:
  trivy image --exit-code 1 --severity HIGH,CRITICAL <image-name>

Pass Criteria:
  - Zero HIGH severity vulnerabilities
  - Zero CRITICAL severity vulnerabilities

Failure Action:
  - Block deployment
  - Create security ticket
  - Require remediation

Scan Frequency:
  - Every build (CI/CD)
  - Daily scan of production images
  - Immediate scan after security advisories

================================================================================
KUBERNETES DEPLOYMENT INTEGRATION
================================================================================

Security Context (Deployment manifest):

spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000

      containers:
      - name: app
        image: registry/app:version
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
              - ALL

        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

        env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password

        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30

        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10

================================================================================
BUILD & DEPLOYMENT WORKFLOW
================================================================================

1. Build:
   docker build -t app:version .

2. Scan:
   trivy image --severity HIGH,CRITICAL app:version

3. Tag:
   docker tag app:version registry/app:version

4. Push:
   docker push registry/app:version

5. Deploy:
   kubectl set image deployment/app app=registry/app:version

6. Verify:
   kubectl rollout status deployment/app

================================================================================
VALIDATION CHECKLIST
================================================================================

Before committing Containerfile:
[ ] Header documentation block included
    [ ] Application name
    [ ] Runtime image documented (registry.access.redhat.com/hi/python:latest)
    [ ] Builder image documented (registry.access.redhat.com/ubi9/python-39:latest)
    [ ] Spec reference included
[ ] Uses approved Red Hat base images
    [ ] Builder stage: registry.access.redhat.com/ubi9/python-39:latest
    [ ] Runtime stage: registry.access.redhat.com/hi/python:latest (PREFERRED)
        OR registry.access.redhat.com/ubi9/python-311:latest (if hardened not suitable)
[ ] Multi-stage build implemented (REQUIRED for hardened images)
[ ] Builder stage uses USER root before dnf install
[ ] Build dependencies include: gcc, postgresql-devel, python3-devel
[ ] dnf cache cleaned: dnf clean all && rm -rf /var/cache/dnf
[ ] Non-root user explicitly set
    [ ] Hardened image: USER 65532 (explicitly set for clarity)
    [ ] UBI image: USER 1001 (explicitly set for clarity)
[ ] File ownership correct
    [ ] Hardened image: --chown=65532:0 for all COPY commands
    [ ] UBI image: --chown=1001:0 for all COPY commands
[ ] No secrets in any layer (ENV vars do NOT contain secrets)
[ ] Environment variables include PYTHONUNBUFFERED=1 and PYTHONDONTWRITEBYTECODE=1
[ ] Minimal packages installed (only venv copied from builder to runtime)
[ ] Health check configured using Python stdlib (works in hardened images)
    [ ] HEALTHCHECK with python -c "import urllib.request; ..." || exit 1
[ ] Production server configured (Gunicorn with logging flags)
    [ ] --access-logfile "-" included
    [ ] --error-logfile "-" included
[ ] Port 8080 exposed (non-privileged port)
[ ] .dockerignore file exists

Before deploying:
[ ] Image builds successfully
[ ] Container scan passes (Trivy)
[ ] Health check endpoint works
[ ] Container runs as non-root (verified)
[ ] No HIGH/CRITICAL vulnerabilities
[ ] Resource limits defined
[ ] Secrets injected at runtime (not in image)

================================================================================
COMMON VIOLATIONS & FIXES
================================================================================

VIOLATION: Running as root
  Bad: No USER directive
  Fix: Add USER appuser before CMD

VIOLATION: Secrets in image
  Bad: COPY credentials.json /app/
  Fix: Mount secrets at runtime (Kubernetes Secrets)

VIOLATION: Using latest tag
  Bad: FROM python:latest
  Fix: FROM python:3.11-slim-bookworm

VIOLATION: No health check
  Bad: Missing HEALTHCHECK
  Fix: Add HEALTHCHECK instruction

VIOLATION: Development server in production
  Bad: CMD ["python", "app.py"]
  Fix: CMD ["gunicorn", "..."]

================================================================================
REFERENCES
================================================================================

WORKING EXAMPLE (REFERENCE IMPLEMENTATION):
  https://github.com/devabm26/python-report-secured/blob/main/Containerfile

  This is a production-grade example demonstrating all requirements:
  - Red Hat hardened image for runtime (registry.access.redhat.com/hi/python:latest)
  - UBI builder stage with proper USER root pattern
  - Complete header documentation
  - Python stdlib HEALTHCHECK (works in hardened images)
  - Gunicorn with container logging flags
  - Proper file ownership (65532:0)
  - All best practices implemented

  When generating Containerfiles, use this as the reference pattern.

SECURITY STANDARDS:
  - Docker Best Practices
  - CIS Docker Benchmark
  - NIST Application Container Security Guide
  - OWASP Docker Security Cheat Sheet
  - Red Hat Container Security Guide

RED HAT HARDENED IMAGES:
  - Image registry: registry.access.redhat.com/hi/
  - Documentation: Red Hat Hummingbird Initiative
  - Distroless-style Python runtime with security hardening

================================================================================
END OF SPECIFICATION
================================================================================
