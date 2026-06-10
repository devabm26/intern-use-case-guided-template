================================================================================
SPECIFICATION: Container Security - Dockerfile Standards
Category: Deployment
Enforcement Level: CRITICAL (BLOCKING)
Version: 2.0
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

PRODUCTION-APPROVED (Red Hat Universal Base Images):
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

FORBIDDEN:
  ❌ python:latest (unpredictable, breaks reproducibility)
  ❌ python:3.8 or older (EOL, no security patches)
  ❌ python:alpine (compatibility issues with psycopg2, numpy, etc.)
  ❌ ubuntu, debian base images (use Red Hat UBI for enterprise)
  ❌ Custom base images (without security approval)
  ❌ Non-Red Hat images in Red Hat OpenShift environments

================================================================================
MANDATORY DOCKERFILE PATTERNS
================================================================================

REQ-1: MULTI-STAGE BUILDS
  Purpose: Minimize final image size, separate build and runtime

  Structure:
    Stage 1: Builder
      - Install build dependencies
      - Build Python packages
      - Create virtual environment

    Stage 2: Runtime
      - Copy only runtime dependencies
      - Copy application code
      - Run as non-root user

REQ-2: NON-ROOT USER
  Rule: Container MUST run as non-root user (UID 1000+)

  Pattern (Red Hat UBI - already non-root):
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

  Note: Red Hat UBI Python images have this built-in - no user creation needed

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

  Pattern:
    HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
      CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

REQ-6: EXPLICIT PORTS
  Rule: EXPOSE ports used by application

  Pattern:
    EXPOSE 8000

REQ-7: PRODUCTION SERVER
  Rule: Use production WSGI/ASGI server (NOT Flask dev server)

  Approved:
    - Gunicorn (Flask, Django)
    - Uvicorn (FastAPI, async)
    - uWSGI (Django)

  Forbidden: flask run, python app.py (development only)

================================================================================
STANDARD DOCKERFILE TEMPLATE (Red Hat UBI)
================================================================================

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

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run with production server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60", "src.app:app"]

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

Before committing Dockerfile:
[ ] Uses approved base image (python:3.11-slim-bookworm or 3.12)
[ ] Multi-stage build implemented
[ ] Non-root user configured (USER directive)
[ ] No secrets in any layer
[ ] Minimal packages installed
[ ] Health check defined
[ ] Production server configured (Gunicorn/Uvicorn)
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

- Docker Best Practices
- CIS Docker Benchmark
- NIST Application Container Security Guide
- OWASP Docker Security Cheat Sheet

================================================================================
END OF SPECIFICATION
================================================================================
