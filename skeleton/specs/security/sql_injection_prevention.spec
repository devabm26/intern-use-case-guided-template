================================================================================
SPECIFICATION: SQL Injection Prevention
Category: Security
Enforcement Level: CRITICAL (BLOCKING)
Version: 2.0
================================================================================

PURPOSE
-------
Eliminate SQL injection vulnerabilities through mandatory parameterized queries.
Ensure 100% of database operations use secure query patterns.

SCOPE
-----
Applies to: ALL database interactions including:
- SELECT queries
- INSERT statements
- UPDATE operations
- DELETE operations
- Stored procedure calls
- Dynamic WHERE clauses
- ORDER BY / LIMIT clauses

================================================================================
MANDATORY REQUIREMENTS
================================================================================

REQ-1: PARAMETERIZED QUERIES ONLY
  Rule: 100% of SQL queries MUST use parameterized statements with placeholders

  ✅ COMPLIANT (PostgreSQL with psycopg2):
    cursor.execute("SELECT * FROM users WHERE email = %s", (user_email,))
    cursor.execute(
        "SELECT * FROM products WHERE category = %s AND price < %s",
        (category, max_price)
    )

  ❌ NON-COMPLIANT:
    cursor.execute(f"SELECT * FROM users WHERE email = '{user_email}'")
    cursor.execute("SELECT * FROM users WHERE id = " + str(user_id))
    cursor.execute("SELECT * FROM users WHERE name = '%s'" % username)

REQ-2: NO STRING FORMATTING IN QUERIES
  Rule: SQL strings SHALL NOT be constructed using:
    - f-strings: f"SELECT {column} FROM {table}"
    - % formatting: "SELECT * FROM users WHERE id = %s" % user_id
    - + concatenation: "SELECT * FROM " + table_name
    - .format(): "SELECT * FROM {}".format(table_name)

  Exception: Column/table names from WHITELISTED constants (not user input)

REQ-3: ORM QUERY BUILDERS PREFERRED
  Rule: Use ORM query builders when available (SQLAlchemy, Django ORM)

  ✅ COMPLIANT (SQLAlchemy):
    session.query(User).filter(User.email == user_email).first()
    session.query(Product).filter(Product.price < max_price).all()

  ✅ COMPLIANT (Django ORM):
    User.objects.filter(email=user_email)
    Product.objects.filter(price__lt=max_price)

  ❌ NON-COMPLIANT (Raw SQL in ORM):
    session.execute(f"SELECT * FROM users WHERE email = '{email}'")

REQ-4: VALIDATE DYNAMIC SQL COMPONENTS
  Rule: If table/column names MUST be dynamic, use STRICT whitelisting

  Pattern (only when absolutely necessary):
    ALLOWED_COLUMNS = {'id', 'name', 'email', 'created_at'}
    ALLOWED_TABLES = {'users', 'products', 'orders'}

    if column not in ALLOWED_COLUMNS:
        raise ValueError(f"Invalid column: {column}")
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table: {table}")

    # Still use parameterized query for values
    query = f"SELECT {column} FROM {table} WHERE id = %s"  # OK: whitelist check
    cursor.execute(query, (record_id,))

REQ-5: ESCAPE IDENTIFIERS WHEN NECESSARY
  Rule: Use database-specific identifier escaping for dynamic identifiers

  PostgreSQL (psycopg2.sql):
    from psycopg2 import sql
    query = sql.SQL("SELECT {field} FROM {table} WHERE id = %s").format(
        field=sql.Identifier(column_name),  # Safely quoted
        table=sql.Identifier(table_name)
    )
    cursor.execute(query, (record_id,))  # Parameters still used for values

================================================================================
DATABASE-SPECIFIC PATTERNS
================================================================================

PostgreSQL (psycopg2):
  Placeholder: %s (for all types)
  Named: %(name)s with dict

  Examples:
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    cursor.execute(
        "SELECT * FROM users WHERE email = %(email)s AND active = %(active)s",
        {'email': user_email, 'active': True}
    )

MySQL (mysql-connector-python):
  Placeholder: %s (format style)

  Examples:
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

SQLite (sqlite3):
  Placeholder: ? (positional) or :name (named)

  Examples:
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    cursor.execute(
        "SELECT * FROM users WHERE email = :email",
        {'email': user_email}
    )

================================================================================
COMMON PATTERNS & SOLUTIONS
================================================================================

PATTERN 1: Single Parameter
  Task: SELECT by ID

  ✅ CORRECT:
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

  ❌ WRONG:
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

PATTERN 2: Multiple Parameters
  Task: SELECT with multiple conditions

  ✅ CORRECT:
    cursor.execute(
        "SELECT * FROM products WHERE category = %s AND price < %s",
        (category, max_price)
    )

  ❌ WRONG:
    cursor.execute(
        f"SELECT * FROM products WHERE category = '{category}' AND price < {max_price}"
    )

PATTERN 3: IN Clause
  Task: SELECT WHERE id IN (list)

  ✅ CORRECT:
    # Generate placeholders for each item
    placeholders = ','.join(['%s'] * len(id_list))
    query = f"SELECT * FROM users WHERE id IN ({placeholders})"
    cursor.execute(query, tuple(id_list))

  Alternative (PostgreSQL):
    cursor.execute("SELECT * FROM users WHERE id = ANY(%s)", (id_list,))

  ❌ WRONG:
    ids = ','.join(map(str, id_list))
    cursor.execute(f"SELECT * FROM users WHERE id IN ({ids})")

PATTERN 4: LIKE Clause
  Task: Partial text search

  ✅ CORRECT:
    search_term = f"%{user_input}%"  # Add wildcards in Python
    cursor.execute("SELECT * FROM users WHERE name LIKE %s", (search_term,))

  ❌ WRONG:
    cursor.execute(f"SELECT * FROM users WHERE name LIKE '%{user_input}%'")

PATTERN 5: INSERT Statement
  Task: Insert new record

  ✅ CORRECT:
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        (name, email)
    )

  ❌ WRONG:
    cursor.execute(f"INSERT INTO users (name, email) VALUES ('{name}', '{email}')")

PATTERN 6: UPDATE Statement
  Task: Update existing record

  ✅ CORRECT:
    cursor.execute(
        "UPDATE users SET email = %s WHERE id = %s",
        (new_email, user_id)
    )

  ❌ WRONG:
    cursor.execute(f"UPDATE users SET email = '{new_email}' WHERE id = {user_id}")

PATTERN 7: DELETE Statement
  Task: Delete record

  ✅ CORRECT:
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

  ❌ WRONG:
    cursor.execute(f"DELETE FROM users WHERE id = {user_id}")

PATTERN 8: ORDER BY (Dynamic Column)
  Task: Sort by user-selected column

  ✅ CORRECT (Whitelist approach):
    ALLOWED_SORT_COLUMNS = {'id', 'name', 'created_at'}
    if sort_column not in ALLOWED_SORT_COLUMNS:
        raise ValueError("Invalid sort column")

    query = f"SELECT * FROM users ORDER BY {sort_column}"  # OK after whitelist
    cursor.execute(query)

  ❌ WRONG:
    cursor.execute(f"SELECT * FROM users ORDER BY {user_input}")  # No whitelist!

================================================================================
ORM PATTERNS (Recommended)
================================================================================

SQLAlchemy (Declarative):
  ✅ CORRECT:
    from sqlalchemy import select
    stmt = select(User).where(User.email == user_email)
    result = session.execute(stmt).scalars().all()

  ✅ CORRECT (Filters):
    users = session.query(User).filter(
        User.email == user_email,
        User.active == True
    ).all()

  ❌ WRONG:
    session.execute(f"SELECT * FROM users WHERE email = '{email}'")

Django ORM:
  ✅ CORRECT:
    users = User.objects.filter(email=user_email, active=True)

  ✅ CORRECT (Complex queries):
    from django.db.models import Q
    users = User.objects.filter(
        Q(email=user_email) | Q(username=user_name)
    )

  ❌ WRONG:
    User.objects.raw(f"SELECT * FROM users WHERE email = '{email}'")

================================================================================
TESTING REQUIREMENTS
================================================================================

TEST-1: SQL Injection Attempt (Manual)
  Input: ' OR '1'='1
  Expected: Query returns no results or error (input treated as literal)

TEST-2: Code Scan for Vulnerable Patterns
  Tool: Bandit, Semgrep, grep
  Patterns to detect:
    - f"SELECT
    - f"INSERT
    - f"UPDATE
    - f"DELETE
    - cursor.execute.*f"
    - cursor.execute.*+
    - cursor.execute.*%.*"

  Pass Criteria: Zero matches

TEST-3: Parameterized Query Verification
  Method: Mock database cursor, verify execute() calls
  Test:
    cursor = Mock()
    query_function(cursor, user_input="'; DROP TABLE users;--")
    cursor.execute.assert_called_with(
        "SELECT * FROM users WHERE name = %s",
        ("'; DROP TABLE users;--",)  # Injected input in params, not query
    )

TEST-4: ORM Query Inspection
  Method: Print SQLAlchemy/Django generated SQL
  Verify: All user inputs appear as bind parameters, not in SQL string

================================================================================
ENFORCEMENT
================================================================================

STATIC ANALYSIS:
  Tool: Bandit (Python security linter)
  Rule: B608 (hardcoded SQL strings)
  Configuration (.bandit):
    tests:
      - B608

  CI/CD: Run bandit in security-scan stage (blocking)

CODE REVIEW:
  Requirement: All database code requires security-focused review
  Checklist:
    [ ] All queries use parameterized statements
    [ ] No f-strings in SQL
    [ ] No string concatenation in SQL
    [ ] Dynamic identifiers use whitelists
    [ ] ORM query builders used where possible

SECURITY TESTS:
  Location: tests/test_security.py
  Coverage: 100% of database query functions
  Gate: Must pass before merge

================================================================================
EXAMPLES OF VULNERABILITIES
================================================================================

VULNERABILITY 1: Classic SQL Injection
  Bad Code:
    email = request.form.get('email')
    cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")

  Attack:
    Email input: ' OR '1'='1' --
    Resulting query: SELECT * FROM users WHERE email = '' OR '1'='1' --'
    Impact: Returns all users

  Fix:
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

VULNERABILITY 2: Second-Order SQL Injection
  Bad Code:
    # First query (safe)
    cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
    username = cursor.fetchone()[0]

    # Second query (vulnerable)
    cursor.execute(f"INSERT INTO logs (message) VALUES ('User {username} logged in')")

  Attack:
    Username in database: admin'; DROP TABLE logs; --
    Resulting query: INSERT INTO logs VALUES ('User admin'; DROP TABLE logs; --logged in')
    Impact: Logs table dropped

  Fix:
    cursor.execute(
        "INSERT INTO logs (message) VALUES (%s)",
        (f"User {username} logged in",)
    )

================================================================================
REFERENCES
================================================================================

- OWASP: SQL Injection
- CWE-89: Improper Neutralization of Special Elements in SQL Command
- psycopg2 documentation: SQL injection protection
- SQLAlchemy documentation: SQL expression language
- Bobby Tables (SQL injection examples)

================================================================================
IMPLEMENTATION CHECKLIST
================================================================================

Before writing database query code:
[ ] Review this specification
[ ] Choose ORM or parameterized queries (never raw string SQL)
[ ] Identify all user inputs that will be used in queries
[ ] Plan how to parameterize each input

While writing code:
[ ] Use %s placeholders for ALL values
[ ] Pass parameters as tuple/dict to execute()
[ ] Use whitelist for dynamic table/column names (if unavoidable)
[ ] Never use f-strings, %, +, or .format() in SQL strings

Before committing:
[ ] Run Bandit: bandit -r src/
[ ] Search for f"SELECT, f"INSERT, f"UPDATE, f"DELETE
[ ] Write security tests for each query function
[ ] Test with malicious input (e.g., ' OR '1'='1)

Before deployment:
[ ] All security tests passing
[ ] Code review by security-aware engineer
[ ] CI/CD security scans passing

================================================================================
END OF SPECIFICATION
================================================================================
