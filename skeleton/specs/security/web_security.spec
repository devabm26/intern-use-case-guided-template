================================================================================
SPECIFICATION: Web Application Security (OWASP Top 10)
Category: Security
Enforcement Level: CRITICAL (BLOCKING)
Version: 2.0
================================================================================

PURPOSE
-------
Implement OWASP Top 10 security controls for all web applications.
Prevent XSS, CSRF, clickjacking, and other web vulnerabilities.

SCOPE
-----
Applies to: All web applications built with Flask, Django, FastAPI, or similar

================================================================================
MANDATORY SECURITY HEADERS
================================================================================

REQ-1: SET SECURITY HEADERS ON ALL RESPONSES
  Rule: Apply security headers to every HTTP response

  Required Headers:

    X-Content-Type-Options: nosniff
      Purpose: Prevent MIME type sniffing
      Value: "nosniff"

    X-Frame-Options: DENY
      Purpose: Prevent clickjacking
      Value: "DENY" or "SAMEORIGIN" (if iframes needed)

    X-XSS-Protection: 1; mode=block
      Purpose: Enable browser XSS filter (legacy browsers)
      Value: "1; mode=block"

    Content-Security-Policy: (see REQ-2)
      Purpose: Prevent XSS, injection, unauthorized resources
      Value: Defined per application requirements

    Strict-Transport-Security: max-age=31536000; includeSubDomains
      Purpose: Enforce HTTPS
      Value: "max-age=31536000; includeSubDomains"
      Note: Production only, requires HTTPS

  Implementation (Flask):
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        if not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        return response

REQ-2: CONTENT SECURITY POLICY (CSP)
  Rule: Define restrictive CSP to prevent XSS and injection attacks

  Baseline CSP (adjust per application needs):
    default-src 'self';
    script-src 'self';
    style-src 'self' 'unsafe-inline';
    img-src 'self' data:;
    font-src 'self';
    connect-src 'self';
    frame-ancestors 'none';

  Notes:
    - Start restrictive, relax only if necessary
    - Avoid 'unsafe-inline' for scripts (XSS risk)
    - Document any relaxations with justification
    - Use nonces or hashes for inline scripts if needed

================================================================================
XSS (CROSS-SITE SCRIPTING) PREVENTION
================================================================================

REQ-3: ENABLE AUTO-ESCAPING IN TEMPLATES
  Rule: Template auto-escaping MUST be enabled (default in Flask/Django)

  Flask (Jinja2):
    - Auto-escaping: Enabled by default
    - Use: {{ variable }} for auto-escaped output
    - Avoid: {{ variable | safe }} unless absolutely necessary

  Django:
    - Auto-escaping: Enabled by default
    - Use: {{ variable }} for auto-escaped output
    - Avoid: {{ variable | safe }} or {% autoescape off %}

  Verification:
    assert app.jinja_env.autoescape == True  # Flask

REQ-4: ESCAPE ALL USER-GENERATED CONTENT
  Rule: ALL user input rendered in HTML MUST be escaped

  ✅ COMPLIANT:
    <p>{{ user.comment }}</p>  # Auto-escaped by Jinja2/Django
    <div>{{ escape(user_input) }}</div>  # Manual escape if needed

  ❌ NON-COMPLIANT:
    <p>{{ user.comment | safe }}</p>  # Bypasses escaping - XSS!
    <div>${user_input}</div>  # Raw interpolation in JavaScript template

REQ-5: VALIDATE AND SANITIZE INPUT
  Rule: Validate input format, sanitize before storage/use

  Pattern:
    from html import escape

    # Validate format
    if not re.match(r'^[a-zA-Z0-9\s]+$', user_input):
        return "Invalid input", 400

    # Escape for safe display
    safe_output = escape(user_input)

REQ-6: NO INLINE JAVASCRIPT
  Rule: Avoid inline JavaScript (violates CSP, increases XSS risk)

  ❌ NON-COMPLIANT:
    <button onclick="deleteUser('{{ user.id }}')">Delete</button>
    <div onerror="maliciousCode()">Content</div>

  ✅ COMPLIANT:
    <button class="delete-btn" data-user-id="{{ user.id }}">Delete</button>
    <script src="/static/js/app.js"></script>  # External script

    // In app.js
    document.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const userId = btn.dataset.userId;
        deleteUser(userId);
      });
    });

================================================================================
CSRF (CROSS-SITE REQUEST FORGERY) PREVENTION
================================================================================

REQ-7: ENABLE CSRF PROTECTION
  Rule: CSRF tokens MUST be validated for state-changing requests

  Flask (Flask-WTF):
    from flask_wtf.csrf import CSRFProtect

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    csrf = CSRFProtect(app)

  Django:
    # CSRF middleware enabled by default
    MIDDLEWARE = [
        'django.middleware.csrf.CsrfViewMiddleware',
        ...
    ]

REQ-8: CSRF TOKENS IN FORMS
  Rule: Include CSRF token in all forms that modify state

  Flask (Jinja2):
    <form method="POST">
      {{ csrf_token() }}
      <!-- form fields -->
    </form>

  Django:
    <form method="POST">
      {% csrf_token %}
      <!-- form fields -->
    </form>

REQ-9: EXEMPT ONLY API/HEALTH ENDPOINTS
  Rule: Exempt CSRF only for read-only or public endpoints

  Flask:
    @app.route('/health')
    @csrf.exempt
    def health():
        return jsonify({'status': 'ok'})

  Note: GET requests exempt by default (but should not modify state)

================================================================================
INPUT VALIDATION
================================================================================

REQ-10: WHITELIST VALIDATION
  Rule: Validate input against allowed patterns/values

  ✅ COMPLIANT:
    ALLOWED_STATUSES = ['APPROVED', 'REJECTED', 'IN_REVIEW']
    status = request.args.get('status', '').upper()
    if status and status not in ALLOWED_STATUSES:
        return jsonify({'error': 'Invalid status'}), 400

  ❌ NON-COMPLIANT:
    status = request.args.get('status')  # No validation
    # Later: SELECT * FROM records WHERE status = %s  # Could be anything

REQ-11: TYPE VALIDATION
  Rule: Validate and convert types with error handling

  ✅ COMPLIANT:
    try:
        limit = int(request.args.get('limit', 100))
        limit = max(1, min(limit, 500))  # Clamp to valid range
    except ValueError:
        return jsonify({'error': 'Invalid limit'}), 400

  ❌ NON-COMPLIANT:
    limit = int(request.args.get('limit'))  # Can raise ValueError
    # Later: No error handling, app crashes

REQ-12: LENGTH VALIDATION
  Rule: Enforce maximum lengths for text inputs

  Pattern:
    MAX_COMMENT_LENGTH = 500
    comment = request.form.get('comment', '')
    if len(comment) > MAX_COMMENT_LENGTH:
        return "Comment too long", 400

================================================================================
SESSION SECURITY
================================================================================

REQ-13: SECURE SESSION CONFIGURATION
  Rule: Configure secure session cookies

  Flask:
    app.config.update(
        SESSION_COOKIE_SECURE=True,      # HTTPS only
        SESSION_COOKIE_HTTPONLY=True,    # No JS access
        SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection
        PERMANENT_SESSION_LIFETIME=3600  # 1 hour timeout
    )

  Django:
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_AGE = 3600

REQ-14: SECRET KEY CONFIGURATION
  Rule: Use strong, random secret key from environment

  ✅ COMPLIANT:
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    if not app.config['SECRET_KEY']:
        raise ValueError("SECRET_KEY must be set")

  Generate with:
    python -c "import secrets; print(secrets.token_hex(32))"

  ❌ NON-COMPLIANT:
    app.config['SECRET_KEY'] = 'dev'  # Hardcoded, weak

================================================================================
AUTHENTICATION & AUTHORIZATION
================================================================================

REQ-15: AUTHENTICATION DECORATORS
  Rule: Protect routes requiring authentication

  Flask:
    from functools import wraps

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    @app.route('/admin')
    @login_required
    def admin():
        ...

REQ-16: AUTHORIZATION CHECKS
  Rule: Verify user permissions before accessing resources

  Pattern:
    @app.route('/resource/<id>')
    @login_required
    def get_resource(id):
        resource = Resource.query.get_or_404(id)
        if resource.owner_id != session['user_id']:
            return "Forbidden", 403
        return render_template('resource.html', resource=resource)

================================================================================
ERROR HANDLING
================================================================================

REQ-17: GENERIC ERROR MESSAGES
  Rule: Don't leak sensitive info in error messages

  ✅ COMPLIANT:
    try:
        user = authenticate(username, password)
    except AuthenticationError:
        return "Invalid credentials", 401  # Generic message

  ❌ NON-COMPLIANT:
    except AuthenticationError as e:
        return f"Error: {str(e)}", 401  # Might leak "User not found" vs "Wrong password"

REQ-18: CUSTOM ERROR PAGES
  Rule: Implement custom error handlers

  Flask:
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', message="Page not found"), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return render_template('error.html', message="Internal error"), 500

================================================================================
LOGGING & MONITORING
================================================================================

REQ-19: LOG SECURITY EVENTS
  Rule: Log authentication, authorization, validation failures

  Events to log:
    - Login attempts (success/failure)
    - Failed authorization checks
    - Input validation failures
    - CSRF token failures
    - Suspicious activity patterns

  Pattern:
    logger.warning(
        "Failed login attempt",
        extra={'username': username, 'ip': request.remote_addr}
    )

REQ-20: NEVER LOG SENSITIVE DATA
  Rule: Don't log passwords, tokens, session IDs, PII

  ❌ NON-COMPLIANT:
    logger.info(f"User logged in with password: {password}")

  ✅ COMPLIANT:
    logger.info(f"User {user_id} logged in successfully")

================================================================================
TESTING REQUIREMENTS
================================================================================

TEST-1: Security Headers Present
  Verify all required headers set on responses

TEST-2: XSS Prevention
  Test malicious input: <script>alert('XSS')</script>
  Verify: Escaped in output as &lt;script&gt;

TEST-3: CSRF Protection
  Test POST without CSRF token
  Verify: 400/403 error returned

TEST-4: Input Validation
  Test invalid status, out-of-range limits
  Verify: 400 errors with descriptive messages

TEST-5: Authentication Required
  Test protected routes without login
  Verify: Redirect to login or 401 error

TEST-6: Authorization Enforced
  Test accessing another user's resource
  Verify: 403 Forbidden

TEST-7: Session Security
  Verify cookies have Secure, HttpOnly, SameSite flags

================================================================================
FRAMEWORK-SPECIFIC IMPLEMENTATION
================================================================================

FLASK (Recommended packages):
  - Flask-WTF: CSRF protection
  - Flask-Login: Session management
  - Flask-Limiter: Rate limiting
  - Flask-Talisman: Security headers

DJANGO (Built-in features):
  - CSRF middleware (enabled by default)
  - Session framework
  - Authentication system
  - Security middleware

FASTAPI:
  - Starlette CSRFMiddleware
  - FastAPI security utilities
  - Pydantic for input validation

================================================================================
DEPLOYMENT CHECKLIST
================================================================================

Before production deployment:
[ ] All security headers configured
[ ] CSP defined and tested
[ ] CSRF protection enabled
[ ] Input validation on all endpoints
[ ] Authentication/authorization implemented
[ ] Session security configured
[ ] HTTPS enforced (HSTS header)
[ ] Error handlers don't leak info
[ ] Security logging enabled
[ ] All security tests passing

================================================================================
REFERENCES
================================================================================

- OWASP Top 10
- OWASP Cheat Sheet Series
- Flask Security Documentation
- Django Security Guide
- CWE/SANS Top 25

================================================================================
END OF SPECIFICATION
================================================================================
