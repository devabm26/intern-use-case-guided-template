================================================================================
SPECIFICATION: Database Connection Layer
Category: Architecture
Enforcement Level: REQUIRED
Version: 2.0
================================================================================

PURPOSE
-------
Define secure, performant database connection patterns for Python applications.

SCOPE
-----
All applications connecting to SQL databases (PostgreSQL, MySQL, SQLite)

================================================================================
MANDATORY REQUIREMENTS
================================================================================

REQ-1: CONNECTION POOLING REQUIRED
  Rule: MUST use connection pooling for all production databases

  Why: Prevents connection exhaustion, improves performance

  Implementation: Use database-specific pooling library
    - PostgreSQL: psycopg2.pool.SimpleConnectionPool
    - MySQL: mysql.connector.pooling.MySQLConnectionPool
    - SQLAlchemy: SQLAlchemy connection pooling

  Configuration:
    - Minimum connections: 1-5 (based on load)
    - Maximum connections: 20-100 (based on database limits)
    - Connection timeout: 30 seconds
    - Idle timeout: 300 seconds

REQ-2: CONTEXT MANAGERS FOR LIFECYCLE
  Rule: MUST use context managers for connection/cursor lifecycle

  Why: Ensures connections always returned to pool, prevents leaks

  Pattern: @contextmanager decorator for automatic cleanup

  Benefits:
    - Automatic resource cleanup
    - Exception-safe connection handling
    - Clear resource boundaries

REQ-3: CENTRALIZED DATABASE CLASS
  Rule: Create single DatabaseConnection class for all database operations

  Responsibilities:
    - Initialize and manage connection pool
    - Provide context manager for connections
    - Execute queries with consistent error handling
    - Close pool on application shutdown

  Location: src/database.py

REQ-4: SEPARATION OF CONCERNS
  Rule: Separate connection management from business logic

  Structure:
    database.py (layer 1): Connection pool, execute methods
    query_functions (layer 2): Domain-specific queries
    routes/controllers (layer 3): HTTP handlers

  Benefits:
    - Testable (mock database layer)
    - Reusable query logic
    - Clear architecture

REQ-5: TYPE HINTS MANDATORY
  Rule: ALL database functions MUST have type annotations

  Required:
    - Parameter types
    - Return types
    - Optional parameters clearly marked

  Why: Enables IDE support, catches errors early, self-documenting

REQ-6: ERROR HANDLING
  Rule: Handle database errors gracefully, log details, don't leak info

  Required handling:
    - Connection failures (log, raise)
    - Query errors (log, handle or raise)
    - Pool exhaustion (log, retry or fail)
    - Transaction failures (log, rollback)

  Logging:
    - Log all connection errors (ERROR level)
    - Log query execution (DEBUG level)
    - Log pool metrics (INFO level)
    - NEVER log query parameter values (may contain sensitive data)

================================================================================
ARCHITECTURE PATTERN
================================================================================

LAYER 1: DatabaseConnection Class
  Purpose: Manage connection pool and provide query execution methods

  Required Methods:
    __init__() → Initialize pool from environment config
    get_connection() → Context manager yielding connection
    execute_query() → Execute SELECT, return list of dicts
    execute_update() → Execute INSERT/UPDATE/DELETE, return row count
    close() → Close all pool connections

LAYER 2: Domain Query Functions
  Purpose: Encapsulate business-specific queries

  Pattern:
    - One function per query type
    - Accept DatabaseConnection as parameter
    - Use parameterized queries (see sql_injection_prevention.spec)
    - Return typed data structures
    - Include docstrings

LAYER 3: Application Integration
  Purpose: Use database layer in application routes/controllers

  Pattern:
    - Initialize DatabaseConnection at startup
    - Import query functions
    - Call query functions from routes
    - Handle application-specific errors
    - Close pool at shutdown

================================================================================
CONFIGURATION REQUIREMENTS
================================================================================

ENVIRONMENT VARIABLES (see secrets_management.spec):
  Required:
    DB_HOST → Database hostname
    DB_NAME → Database name
    DB_USER → Database username
    DB_PASSWORD → Database password (from secrets manager)

  Optional:
    DB_PORT → Port number (default: 5432 for PostgreSQL)
    DB_POOL_MIN → Minimum pool connections (default: 1)
    DB_POOL_MAX → Maximum pool connections (default: 20)
    DB_TIMEOUT → Connection timeout seconds (default: 30)

VALIDATION:
  - Verify all required variables set at startup
  - Raise ValueError with clear message if missing
  - Fail fast (don't start app with invalid config)

================================================================================
QUERY EXECUTION PATTERNS
================================================================================

PATTERN 1: SELECT Queries
  Method: execute_query()
  Returns: List[Dict[str, Any]]
  Usage: Read operations only
  Features:
    - Parameterized query
    - Returns dict cursor results
    - Automatic connection cleanup

PATTERN 2: INSERT/UPDATE/DELETE
  Method: execute_update()
  Returns: int (rows affected)
  Usage: Write operations
  Features:
    - Parameterized query
    - Transaction commit
    - Automatic rollback on error

PATTERN 3: Transactions
  Method: Custom context manager
  Usage: Multiple operations in single transaction
  Features:
    - BEGIN/COMMIT/ROLLBACK
    - Isolation from other operations
    - All-or-nothing semantics

================================================================================
SECURITY REQUIREMENTS
================================================================================

MANDATORY (see related specs):
  - specs/security/secrets_management.spec
    → No hardcoded credentials
    → Load from environment variables

  - specs/security/sql_injection_prevention.spec
    → 100% parameterized queries
    → No string formatting in SQL

  - Principle of least privilege
    → Use read-only database user when possible
    → Grant only required permissions

  - Connection encryption
    → Use SSL/TLS for production databases
    → Verify server certificates

================================================================================
TESTING REQUIREMENTS
================================================================================

REQUIRED TESTS (see specs/testing/security_tests.spec):

  TEST-1: Connection Initialization
    - Valid config → successful pool creation
    - Missing config → ValueError raised
    - Invalid credentials → connection error

  TEST-2: Query Execution
    - Parameterized queries verified
    - Results returned as expected type
    - Errors handled appropriately

  TEST-3: Connection Lifecycle
    - Connections acquired from pool
    - Connections returned after use
    - Pool closes cleanly

  TEST-4: Error Scenarios
    - Query syntax errors
    - Connection timeouts
    - Pool exhaustion

================================================================================
IMPLEMENTATION CHECKLIST
================================================================================

Before implementing:
[ ] Review specs/security/secrets_management.spec
[ ] Review specs/security/sql_injection_prevention.spec
[ ] Identify required database operations
[ ] Plan query functions needed

During implementation:
[ ] Create DatabaseConnection class
[ ] Implement connection pooling
[ ] Implement context managers
[ ] Create query execution methods
[ ] Add error handling and logging
[ ] Write domain query functions

Before committing:
[ ] All functions have type hints
[ ] No hardcoded credentials exist
[ ] All queries use parameterized statements
[ ] Error handling covers common failures
[ ] Tests written for all query functions
[ ] Documentation complete

================================================================================
ANTI-PATTERNS TO AVOID
================================================================================

❌ Creating new connection for every query (use pooling)
❌ Not closing connections (use context managers)
❌ Hardcoding credentials (use environment variables)
❌ String formatting in SQL (use parameterized queries)
❌ Ignoring errors (log and handle appropriately)
❌ Database logic in route handlers (use query functions)
❌ Mocking database in integration tests (test against real DB)

================================================================================
PERFORMANCE CONSIDERATIONS
================================================================================

Connection Pool Sizing:
  Formula: connections = ((core_count * 2) + effective_spindle_count)
  Adjust based on:
    - Application concurrency
    - Database connection limits
    - Network latency
    - Query complexity

Query Optimization:
  - Use appropriate indexes
  - Avoid N+1 query problems
  - Use LIMIT for large result sets
  - Consider pagination for lists

Connection Reuse:
  - Pool connections reused across requests
  - Avoid creating connection per request
  - Monitor pool utilization metrics

================================================================================
MONITORING & OBSERVABILITY
================================================================================

REQUIRED METRICS:
  - Active connections count
  - Idle connections count
  - Connection wait time
  - Query execution time
  - Error rate by query type

LOGGING:
  - Connection pool initialization (INFO)
  - Connection acquisition/release (DEBUG)
  - Query execution time > threshold (WARNING)
  - All database errors (ERROR)
  - Pool exhaustion events (CRITICAL)

================================================================================
END OF SPECIFICATION
================================================================================
