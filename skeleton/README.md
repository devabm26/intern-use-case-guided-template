# ${{ values.component_id }}

**Generated from Enterprise Python Application Template**  
**Owner:** ${{ values.owner }}  
**Description:** ${{ values.description }}

---

## 🚀 Quick Start

This application was generated from the enterprise golden path template with built-in security guardrails.

### Prerequisites
- Python 3.11+ or 3.12+
- PostgreSQL (for database connectivity)
- Docker or Podman (for containerization)
- Access to Red Hat OpenShift or Kubernetes cluster (for deployment)
- Access to Red Hat Container Registry (registry.access.redhat.com) - free, no authentication required

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ${{ values.component_id }}
   ```

2. **Set up environment**
   ```bash
   cp config/.env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Run database migrations** (if applicable)
   ```bash
   # Add migration commands here
   ```

5. **Start the application**
   ```bash
   python -m src.app
   # Or use: flask run --debug (development only)
   ```

6. **Access the application**
   - Local: http://localhost:8000
   - Health check: http://localhost:8000/health

---

## 📋 Required Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Application
SECRET_KEY=<generate-with-python-secrets-token-hex-32>
FLASK_ENV=development

# Database
DB_HOST=${{ values.db_host }}
DB_NAME=${{ values.db_name }}
DB_USER=<from-secrets-manager>
DB_PASSWORD=<from-secrets-manager>
DB_PORT=5432

# Logging
LOG_LEVEL=INFO
```

**NEVER commit `.env` file to version control!**

### Generating SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🏗️ Project Structure

```
${{ values.component_id }}/
├── src/                     # Application source code
│   ├── app.py              # Application entry point
│   ├── config.py           # Configuration management
│   ├── database.py         # Database layer
│   ├── routes.py           # HTTP endpoints
│   └── templates/          # HTML templates
├── tests/                  # Test suite
│   ├── test_security.py    # Security tests (REQUIRED)
│   └── test_app.py         # Application tests
├── config/                 # Configuration files
│   └── .env.example        # Environment variable template
├── specs/                  # Implementation specifications
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies (pinned)
├── Dockerfile              # Container definition
└── README.md              # This file
```

**Note:** CI/CD configuration not included - implement per your platform.  
See `specs/deployment/ci_cd_pipeline.spec` for requirements.

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Security Tests Only
```bash
pytest tests/test_security.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Security Scanning
```bash
# Check for hardcoded secrets
detect-secrets scan --all-files

# Scan dependencies for vulnerabilities
pip-audit -r requirements.txt

# Generate SBOM
cyclonedx-py requirements -r requirements.txt -o sbom.json
```

---

## 🐳 Container Build

This application uses **Red Hat Universal Base Images (UBI)** for enterprise-grade security:
- ✅ Free to use and redistribute
- ✅ Security updates from Red Hat
- ✅ Already runs as non-root (UID 1001)
- ✅ Optimized for OpenShift/Kubernetes
- ✅ No authentication required for pulling

### Build Image
```bash
docker build -t ${{ values.component_id }}:latest .
# Or use Podman (Red Hat's container tool)
podman build -t ${{ values.component_id }}:latest .
```

### Run Container Locally
```bash
docker run -p 8000:8000 \
  -e DB_HOST=$DB_HOST \
  -e DB_NAME=$DB_NAME \
  -e DB_USER=$DB_USER \
  -e DB_PASSWORD=$DB_PASSWORD \
  -e SECRET_KEY=$SECRET_KEY \
  ${{ values.component_id }}:latest
```

### Scan Container for Vulnerabilities
```bash
trivy image --severity HIGH,CRITICAL ${{ values.component_id }}:latest
```

---

## 🚢 Deployment

### Prerequisites
- Kubernetes cluster access
- Secrets configured (database credentials, SECRET_KEY)
- Container registry access

### Deploy to Staging
```bash
# Via GitLab CI/CD (automated)
# Push to main branch → triggers staging deployment

# Manual deployment
kubectl set image deployment/${{ values.component_id }} \
  ${{ values.component_id }}=registry/app:$TAG -n staging
```

### Deploy to Production
```bash
# Via GitLab CI/CD (manual approval required)
# Tag release → approve deployment in pipeline

# Manual deployment
kubectl set image deployment/${{ values.component_id }} \
  ${{ values.component_id }}=registry/app:$TAG -n production
```

---

## 🔒 Security

This application implements enterprise security standards:

- ✅ **Zero Hardcoded Secrets** - All credentials from environment
- ✅ **SQL Injection Prevention** - 100% parameterized queries
- ✅ **XSS Prevention** - Auto-escaped templates
- ✅ **CSRF Protection** - Enabled for all state-changing requests
- ✅ **Security Headers** - CSP, X-Frame-Options, etc.
- ✅ **Container Security** - Non-root user, minimal attack surface
- ✅ **Dependency Scanning** - Automated CVE detection
- ✅ **SBOM Generation** - Software bill of materials

### Security Specifications

All security requirements are documented in `specs/security/`:
- `secrets_management.spec` - Credential handling
- `sql_injection_prevention.spec` - Database security
- `web_security.spec` - OWASP Top 10 controls
- `dependency_management.spec` - Supply chain security

### Security Testing

Security tests MUST pass before deployment:
```bash
pytest tests/test_security.py -v
```

---

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-06-10T10:00:00Z"
}
```

### Metrics to Monitor
- Request latency
- Error rate
- Database connection pool utilization
- Memory usage
- CPU usage

---

## 🔄 CI/CD Pipeline

The GitLab CI/CD pipeline includes:

1. **Security Scan** (blocking)
   - Secret detection
   - Dependency vulnerability scan
   - SBOM generation
   - Static code analysis

2. **Test** (blocking)
   - Unit tests
   - Security tests
   - Code coverage (≥80% required)

3. **Build** (blocking)
   - Container build
   - Container vulnerability scan
   - Image push to registry

4. **Deploy** (manual approval)
   - Staging deployment (automated after build)
   - Production deployment (requires approval)

---

## 📚 Documentation

- **Enterprise Standards**: `docs/ENTERPRISE_STANDARDS.md`
- **AI Development Guide**: `CLAUDE.md`
- **Specifications**: `specs/` directory
  - `specs/security/` - Security requirements
  - `specs/architecture/` - Architecture patterns
  - `specs/testing/` - Testing requirements
  - `specs/deployment/` - Deployment standards

---

## 🛠️ Development Guidelines

### For AI-Assisted Development

This project has **built-in AI guardrails**. Compliance level depends on your AI tool:

#### 🟢 Claude Code (Automatic)
When using **Claude Code**, AI compliance is semi-automatic:
- ✅ Auto-loads `.claude/project-instructions.md`
- ✅ Automatically reads specs before coding
- ✅ Follows security patterns by default

**Just describe your task normally:**
```
You: "Add endpoint to list all approved thoughts"
Claude: [reads specs, implements securely]
```

#### 🟡 Other AI Tools (Manual Prompting Required)
For **GitHub Copilot, ChatGPT, etc.**, you MUST prompt explicitly:

**❌ BAD:** "Create database queries"

**✅ GOOD:** 
```
Create database queries.
MANDATORY: Read specs/security/sql_injection_prevention.spec first.
Use parameterized queries only, no string formatting.
```

**📖 See `docs/PROMPTING_GUIDE.md` for template prompts.**

#### 📋 AI Development Checklist (All Tools)
1. Read `CLAUDE.md` for security rules
2. Read applicable `specs/` before implementing
3. Never hardcode secrets
4. Always use parameterized SQL queries
5. Validate all user inputs
6. Escape all outputs
7. Write security tests

### Code Review Checklist

Before merging:
- [ ] All tests passing
- [ ] Security tests passing
- [ ] No hardcoded secrets
- [ ] All queries parameterized
- [ ] Input validation implemented
- [ ] Security headers configured
- [ ] Dependencies scanned
- [ ] Code coverage ≥80%

---

## 🐛 Troubleshooting

### Application won't start
- Check environment variables are set (`.env` file exists)
- Verify database is accessible
- Check SECRET_KEY is configured

### Database connection fails
- Verify DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
- Check database is running
- Verify network connectivity

### Container scan fails
- Update base image: `python:3.11-slim-bookworm` or `python:3.12-slim-bookworm`
- Update dependencies with security patches
- Review Trivy report for specific CVEs

### Security tests fail
- Review test output for specific failure
- Check specifications in `specs/security/`
- Verify security controls are implemented

---

## 📞 Support

- **Security Questions**: #security-guild
- **Platform/Infrastructure**: #platform-engineering
- **Code Review**: #development-team
- **On-Call**: PagerDuty escalation

---

## 📄 License

[Add your license information]

---

## 🤝 Contributing

1. Create feature branch from `main`
2. Implement changes following specs in `specs/`
3. Write tests (including security tests)
4. Run security scans locally
5. Create merge request
6. Await code review approval
7. Merge after CI/CD pipeline passes

---

**Generated:** {{ "now" | date("YYYY-MM-DD") }}  
**Template Version:** 2.0  
**Compliance:** Enterprise Security Standards v2.0
