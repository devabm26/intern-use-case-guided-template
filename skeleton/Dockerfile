# Multi-stage build for secure Python dashboard
# Base image: APPROVED - Red Hat UBI 9 with Python 3.11 (enterprise-grade, security-patched)

# Stage 1: Builder
FROM registry.access.redhat.com/ubi9/python-311:latest AS builder

# Install build dependencies
RUN dnf install -y \
    gcc \
    postgresql-devel && \
    dnf clean all

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM registry.access.redhat.com/ubi9/python-311:latest

# Install runtime dependencies only
RUN dnf install -y \
    postgresql && \
    dnf clean all

# Note: Red Hat UBI Python images already run as non-root user (UID 1001)
# This is a built-in security feature of Red Hat Enterprise images

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code (UBI default user is UID 1001)
COPY --chown=1001:0 src/ /app/src/
COPY --chown=1001:0 config/ /app/config/

# UBI images already run as non-root, explicitly set for clarity
USER 1001

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run with Gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60", "src.app:app"]
