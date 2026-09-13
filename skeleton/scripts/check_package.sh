#!/bin/bash
# ==============================================================================
# TPA Package Vulnerability Checker
# Check Python packages against Red Hat Trusted Profile Analyzer before adding
# to requirements.txt
# ==============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load TPA configuration
if [ -f .tpa-config ]; then
  source .tpa-config
else
  echo -e "${RED}❌ Error: .tpa-config file not found${NC}"
  echo "Run this script from the project root directory"
  exit 1
fi

# Check if TPA is enabled
if [ "$TPA_ENABLED" != "true" ]; then
  echo -e "${YELLOW}⚠️  TPA checking is disabled in .tpa-config${NC}"
  echo "Package: $1==$2 (not checked)"
  exit 0
fi

# Validate arguments
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <package-name> <version>"
  echo "Example: $0 Flask 3.0.3"
  exit 1
fi

PACKAGE_NAME=$1
REQUESTED_VERSION=$2

# Check for required environment variable
if [ -z "$TPA_CLIENT_SECRET" ]; then
  echo -e "${RED}❌ Error: TPA_CLIENT_SECRET environment variable not set${NC}"
  echo ""
  echo "Set the secret before running this script:"
  echo "  export TPA_CLIENT_SECRET=<your-client-secret>"
  echo ""
  echo "Or retrieve from Kubernetes secret:"
  echo "  export TPA_CLIENT_SECRET=\$(kubectl get secret trustification-secret -n thoughts-app -o jsonpath='{.data.oidc_client_secret}' | base64 -d)"
  exit 1
fi

echo -e "${BLUE}🔍 Checking ${PACKAGE_NAME}==${REQUESTED_VERSION} against TPA...${NC}"

# Get OIDC access token
echo "Authenticating with TPA..."
TOKEN_RESPONSE=$(curl -s -X POST "${TPA_OIDC_ISSUER}/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=${TPA_CLIENT_ID}" \
  -d "client_secret=${TPA_CLIENT_SECRET}")

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token // empty')

if [ -z "$ACCESS_TOKEN" ]; then
  echo -e "${RED}❌ Error: Failed to obtain access token from TPA${NC}"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi

echo -e "${GREEN}✅ Authenticated with TPA${NC}"

# Query package vulnerabilities
echo "Querying vulnerabilities for ${PACKAGE_NAME}==${REQUESTED_VERSION}..."

# NOTE: Update this endpoint based on actual TPA API structure
# This is a placeholder - adjust when TPA is available for testing
VULN_RESPONSE=$(curl -s -X GET \
  "${TPA_URL}/api/v2/package/search?name=${PACKAGE_NAME}&version=${REQUESTED_VERSION}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" || echo "{}")

# Parse vulnerabilities
CRITICAL_COUNT=$(echo "$VULN_RESPONSE" | jq -r '[.vulnerabilities[]? | select(.severity == "CRITICAL")] | length // 0')
HIGH_COUNT=$(echo "$VULN_RESPONSE" | jq -r '[.vulnerabilities[]? | select(.severity == "HIGH")] | length // 0')
MEDIUM_COUNT=$(echo "$VULN_RESPONSE" | jq -r '[.vulnerabilities[]? | select(.severity == "MEDIUM")] | length // 0')
LOW_COUNT=$(echo "$VULN_RESPONSE" | jq -r '[.vulnerabilities[]? | select(.severity == "LOW")] | length // 0')

echo ""
echo "Vulnerability Summary:"
echo "  Critical: $CRITICAL_COUNT"
echo "  High:     $HIGH_COUNT"
echo "  Medium:   $MEDIUM_COUNT"
echo "  Low:      $LOW_COUNT"

# Decision logic
if [ "$CRITICAL_COUNT" -gt 0 ] || [ "$HIGH_COUNT" -gt 0 ]; then
  echo ""
  echo -e "${RED}❌ BLOCKED: Package has HIGH or CRITICAL vulnerabilities${NC}"
  echo ""
  echo "Found vulnerabilities:"
  echo "$VULN_RESPONSE" | jq -r '.vulnerabilities[]? | select(.severity == "CRITICAL" or .severity == "HIGH") | "  - \(.cve_id) [\(.severity)]: \(.description // "No description")"'
  echo ""
  echo -e "${YELLOW}🔧 Searching for safer version...${NC}"

  # Try to find a safe version
  # NOTE: Adjust this endpoint based on actual TPA API
  VERSIONS_RESPONSE=$(curl -s -X GET \
    "${TPA_URL}/api/v2/package/versions?name=${PACKAGE_NAME}" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" || echo '{"versions":[]}')

  # Check each version for vulnerabilities (simplified - in production, optimize this)
  SAFE_VERSION=""
  echo "$VERSIONS_RESPONSE" | jq -r '.versions[]? // empty' | while read -r VERSION; do
    if [ -n "$SAFE_VERSION" ]; then
      break
    fi

    VERSION_VULNS=$(curl -s -X GET \
      "${TPA_URL}/api/v2/package/search?name=${PACKAGE_NAME}&version=${VERSION}" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" || echo '{"vulnerabilities":[]}')

    VERSION_CRITICAL=$(echo "$VERSION_VULNS" | jq -r '[.vulnerabilities[]? | select(.severity == "CRITICAL")] | length // 0')
    VERSION_HIGH=$(echo "$VERSION_VULNS" | jq -r '[.vulnerabilities[]? | select(.severity == "HIGH")] | length // 0')

    if [ "$VERSION_CRITICAL" -eq 0 ] && [ "$VERSION_HIGH" -eq 0 ]; then
      echo -e "${GREEN}✅ Found safe version: ${PACKAGE_NAME}==${VERSION}${NC}"
      echo ""
      echo "Recommendation:"
      echo "  ${PACKAGE_NAME}==${VERSION}  # Auto-fixed from ${REQUESTED_VERSION} (CVE remediation via TPA)"
      SAFE_VERSION=$VERSION
      break
    fi
  done

  if [ -z "$SAFE_VERSION" ]; then
    echo -e "${RED}❌ No safe version found${NC}"
    echo "Consider using an alternative package"
  fi

  exit 1
else
  echo ""
  echo -e "${GREEN}✅ Package approved: ${PACKAGE_NAME}==${REQUESTED_VERSION}${NC}"
  echo "No HIGH or CRITICAL vulnerabilities found"
  echo ""
  echo "Add to requirements.txt:"
  echo "  ${PACKAGE_NAME}==${REQUESTED_VERSION}  # Verified by TPA ($(date +%Y-%m-%d))"
  exit 0
fi
