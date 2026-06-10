================================================================================
SPECIFICATION: Web Application Architecture
Category: Architecture
Enforcement Level: REQUIRED
Version: 2.0
================================================================================

PURPOSE
-------
Define standard architecture patterns for Python web applications.

SCOPE
-----
All web applications built with Flask, Django, FastAPI, or similar frameworks

================================================================================
PROJECT STRUCTURE (MANDATORY)
================================================================================

Standard Directory Layout:

project-root/
├── src/                        # Application source code
│   ├── __init__.py
│   ├── app.py                  # Application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database layer (see database_layer.spec)
│   ├── routes.py or views.py   # HTTP endpoints/controllers
│   ├── models.py               # Data models/entities
│   ├── templates/              # HTML templates (if applicable)
│   ├── static/                 # CSS, JS, images (if applicable)
│   └── utils/                  # Shared utilities
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_security.py        # Security tests (REQUIRED)
│   ├── test_routes.py          # Route/endpoint tests
│   └── test_database.py        # Database layer tests
├── config/                     # Configuration files
│   ├── .env.example            # Environment variable template
│   └── [application-specific configs]
├── specs/                      # Implementation specifications
│   ├── security/
│   ├── architecture/
│   ├── testing/
│   └── deployment/
├── docs/                       # Documentation
│   └── ENTERPRISE_STANDARDS.md
├── requirements.txt            # Python dependencies (pinned)
├── Dockerfile                  # Container definition
├── .gitlab-ci.yml             # CI/CD pipeline
├── .gitignore                 # Git ignore patterns
├── CLAUDE.md                  # AI development guidelines
└── README.md                  # Project documentation

================================================================================
APPLICATION INITIALIZATION (REQUIRED PATTERN)
================================================================================

STRUCTURE: src/app.py

Required Components:
  1. Environment variable loading (python-dotenv)
  2. Logging configuration
  3. Framework initialization (Flask/Django/FastAPI)
  4. Secret key validation (see secrets_management.spec)
  5. Database connection initialization (see database_layer.spec)
  6. Security middleware/decorators (see web_security.spec)
  7. Route registration
  8. Error handlers

Startup Sequence:
  1. Load environment variables
  2. Configure logging
  3. Validate required configuration
  4. Initialize framework app
  5. Initialize database connection
  6. Register security middleware
  7. Register routes
  8. Register error handlers
  9. Start application

Shutdown Sequence:
  1. Close database connections
  2. Flush logs
  3. Clean up temporary resources

================================================================================
CONFIGURATION MANAGEMENT
================================================================================

PATTERN: src/config.py

Required Functionality:
  - Load environment variables
  - Validate required settings
  - Provide type-safe configuration access
  - Support multiple environments (dev, staging, prod)

Configuration Sources (priority order):
  1. Environment variables (highest)
  2. Configuration files
  3. Default values in code (non-sensitive only)

Validation:
  - Fail fast on missing required configuration
  - Raise ValueError with descriptive messages
  - Log configuration loaded (but NOT values)

================================================================================
ROUTING / ENDPOINTS
================================================================================

STRUCTURE: src/routes.py (Flask) or src/views.py (Django)

Required Patterns:
  - One route/view per logical operation
  - Input validation on all routes (see web_security.spec)
  - Authentication/authorization decorators where needed
  - Consistent error handling
  - Consistent response format (JSON APIs)

Route Responsibilities:
  1. Parse and validate input
  2. Call business logic/query functions
  3. Format response
  4. Handle errors appropriately

Route Should NOT:
  - Contain database logic (use query functions)
  - Contain complex business logic (extract to services)
  - Hardcode values (use configuration)

================================================================================
TEMPLATE LAYER (if applicable)
================================================================================

LOCATION: src/templates/

Requirements:
  - Auto-escaping MUST be enabled (see web_security.spec)
  - No inline JavaScript (CSP compliance)
  - Responsive design (mobile-friendly)
  - Accessibility (WCAG 2.1 Level AA minimum)

Template Organization:
  - base.html: Base layout
  - Specific templates: Extend base
  - Partials: Reusable components
  - Error templates: Custom error pages

================================================================================
STATIC ASSETS (if applicable)
================================================================================

LOCATION: src/static/

Organization:
  static/
  ├── css/
  ├── js/
  ├── images/
  └── fonts/

Requirements:
  - Serve from same origin (CSP compliance)
  - Minify for production
  - Version/hash for cache busting
  - No sensitive data in client-side code

================================================================================
ERROR HANDLING
================================================================================

REQUIRED ERROR HANDLERS:

HTTP 400 (Bad Request):
  - Trigger: Invalid input, validation failure
  - Response: Generic error message (don't leak validation details)
  - Log: Input validation failure details

HTTP 401 (Unauthorized):
  - Trigger: Missing or invalid authentication
  - Response: "Authentication required"
  - Log: Failed authentication attempt

HTTP 403 (Forbidden):
  - Trigger: Insufficient permissions
  - Response: "Access denied"
  - Log: Authorization failure

HTTP 404 (Not Found):
  - Trigger: Resource not found
  - Response: Generic "Not found" message
  - Log: Requested path (if suspicious)

HTTP 500 (Internal Server Error):
  - Trigger: Unhandled exception
  - Response: Generic error message (NEVER leak stack traces)
  - Log: Full exception details with stack trace

Error Response Format (JSON APIs):
  {
    "error": "Human-readable message",
    "code": "ERROR_CODE_CONSTANT",
    "request_id": "unique-request-id"
  }

================================================================================
LOGGING CONFIGURATION
================================================================================

REQUIRED:
  - Structured logging (JSON format preferred)
  - Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
  - Include timestamp, level, module, message
  - Log request IDs for tracing
  - Rotate logs (size-based or time-based)

What to Log:
  - Application startup/shutdown (INFO)
  - Request/response (DEBUG)
  - Authentication events (INFO)
  - Authorization failures (WARNING)
  - Validation failures (WARNING)
  - Database errors (ERROR)
  - Unhandled exceptions (ERROR/CRITICAL)

What NOT to Log:
  - Passwords, tokens, secrets
  - Sensitive user data (PII)
  - Full credit card numbers
  - Session IDs

================================================================================
SECURITY MIDDLEWARE (MANDATORY)
================================================================================

Required (see specs/security/web_security.spec):
  - Security headers (@after_request hook)
  - CSRF protection
  - Session security
  - Rate limiting (recommended)
  - Request size limits

Flask Example Structure:
  @app.after_request
  def set_security_headers(response):
      # Set all required security headers
      return response

  csrf = CSRFProtect(app)

Django: Use built-in middleware + django-csp

================================================================================
HEALTH CHECK ENDPOINT (REQUIRED)
================================================================================

Route: GET /health

Purpose: Container orchestration health checks

Required Checks:
  - Application running
  - Database connectivity
  - Critical dependencies available

Response:
  Success (200):
    {
      "status": "healthy",
      "timestamp": "ISO-8601",
      "checks": {
        "database": "ok",
        "cache": "ok"
      }
    }

  Failure (503):
    {
      "status": "unhealthy",
      "timestamp": "ISO-8601",
      "checks": {
        "database": "failed",
        "cache": "ok"
      }
    }

Security:
  - Exempt from CSRF (@csrf.exempt)
  - No authentication required
  - Don't leak sensitive info

================================================================================
API RESPONSE PATTERNS
================================================================================

SUCCESS Response:
  {
    "data": [...],
    "count": 100,
    "pagination": {...}  // if applicable
  }

ERROR Response:
  {
    "error": "Descriptive message",
    "code": "VALIDATION_FAILED",
    "details": {...}  // optional, don't leak sensitive info
  }

Pagination:
  {
    "data": [...],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 500,
      "total_pages": 25
    }
  }

================================================================================
TESTING INTEGRATION
================================================================================

Test Organization:
  - Mirror src/ structure in tests/
  - test_[module].py for each module
  - Fixtures in conftest.py
  - Separate integration vs unit tests

Required Test Coverage:
  - Routes/views: 100% (all endpoints)
  - Security controls: 100% (critical)
  - Database layer: 100%
  - Business logic: 80% minimum

Test Types:
  - Unit tests: Isolated component testing
  - Integration tests: Database + app integration
  - Security tests: OWASP controls verification
  - End-to-end tests: Full user flows

================================================================================
ENVIRONMENT-SPECIFIC CONFIGURATION
================================================================================

DEVELOPMENT:
  - Debug mode enabled
  - Detailed error pages
  - Hot reload enabled
  - Relaxed security (where safe)
  - Local .env file

STAGING:
  - Production-like configuration
  - Debug mode disabled
  - Security headers enforced
  - Kubernetes Secrets
  - Monitoring enabled

PRODUCTION:
  - Debug mode disabled
  - Generic error pages
  - All security controls enforced
  - Vault/Secrets Manager
  - Full monitoring and alerting
  - HTTPS enforced (HSTS)

================================================================================
IMPLEMENTATION CHECKLIST
================================================================================

Before implementation:
[ ] Review all specs/ specifications
[ ] Understand application requirements
[ ] Choose appropriate framework
[ ] Plan route structure

During implementation:
[ ] Follow project structure standard
[ ] Initialize app with all required components
[ ] Implement security middleware
[ ] Create health check endpoint
[ ] Add error handlers
[ ] Configure logging
[ ] Write tests as you go

Before deployment:
[ ] All security tests passing
[ ] All routes tested
[ ] Error handlers tested
[ ] Health check verified
[ ] Configuration validated
[ ] Documentation complete

================================================================================
FRAMEWORK-SPECIFIC NOTES
================================================================================

FLASK:
  - Use application factory pattern
  - Blueprint for route organization
  - Flask-WTF for CSRF
  - Flask-Login for auth (if needed)
  - Gunicorn for production

DJANGO:
  - Use settings.py properly
  - Apps for feature organization
  - Built-in CSRF middleware
  - Built-in auth system
  - Django security middleware

FASTAPI:
  - Async/await patterns
  - Pydantic for validation
  - Dependency injection
  - Automatic API docs (Swagger)
  - Uvicorn for production

================================================================================
END OF SPECIFICATION
================================================================================
