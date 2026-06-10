#!/bin/bash
################################################################################
# Context Loader for OpenShift Dev Spaces + AI Assistants
#
# Purpose: Load project compliance context for AI assistants that don't
#          automatically read .claude/ directory (e.g., Vertex AI Claude)
#
# Usage: Run this script, then paste output into AI chat to provide context
################################################################################

echo "================================================================================"
echo "PROJECT COMPLIANCE CONTEXT FOR AI ASSISTANT"
echo "================================================================================"
echo ""
echo "This is an ENTERPRISE Python application with MANDATORY security compliance."
echo "You MUST follow all specifications before writing any code."
echo ""
echo "================================================================================"
echo "CRITICAL SECURITY RULES (NON-NEGOTIABLE)"
echo "================================================================================"
echo ""

# Load critical rules from CLAUDE.md
if [ -f "CLAUDE.md" ]; then
    echo "From CLAUDE.md:"
    echo ""
    grep -A 3 "ABSOLUTE RULE:" CLAUDE.md | head -20
    echo ""
fi

echo "================================================================================"
echo "PROJECT INSTRUCTIONS"
echo "================================================================================"
echo ""

# Load project instructions
if [ -f ".claude/project-instructions.md" ]; then
    cat .claude/project-instructions.md
else
    echo "ERROR: .claude/project-instructions.md not found!"
fi

echo ""
echo "================================================================================"
echo "AVAILABLE SPECIFICATIONS"
echo "================================================================================"
echo ""
echo "Security Specifications:"
ls -1 specs/security/*.spec 2>/dev/null | sed 's/^/  - /'
echo ""
echo "Architecture Specifications:"
ls -1 specs/architecture/*.spec 2>/dev/null | sed 's/^/  - /'
echo ""
echo "Testing Specifications:"
ls -1 specs/testing/*.spec 2>/dev/null | sed 's/^/  - /'
echo ""
echo "Deployment Specifications:"
ls -1 specs/deployment/*.spec 2>/dev/null | sed 's/^/  - /'
echo ""

echo "================================================================================"
echo "QUICK REFERENCE"
echo "================================================================================"
echo ""
echo "Before implementing ANY feature, you MUST:"
echo "  1. Read applicable specification files from specs/"
echo "  2. Follow the ✅ APPROVED patterns"
echo "  3. Avoid the ❌ FORBIDDEN patterns"
echo "  4. Implement required security tests"
echo ""
echo "For specific tasks, read:"
echo "  - Database work: specs/architecture/database_layer.spec"
echo "  - Web routes: specs/architecture/web_application.spec"
echo "  - SQL queries: specs/security/sql_injection_prevention.spec"
echo "  - Credentials: specs/security/secrets_management.spec"
echo "  - Container: specs/deployment/dockerfile.spec"
echo ""
echo "================================================================================"
echo "COPY THE ABOVE CONTEXT INTO YOUR AI CHAT BEFORE STARTING"
echo "================================================================================"
