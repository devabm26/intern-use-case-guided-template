# TPA Package Vulnerability Checking

## Overview

This directory contains scripts for checking Python package vulnerabilities against Red Hat Trusted Profile Analyzer (TPA) before adding them to `requirements.txt`.

## Setup

1. **Configure TPA settings** in `.tpa-config` (automatically configured by Backstage template)

2. **Set TPA client secret** from environment or Kubernetes:
   ```bash
   # From Kubernetes secret
   export TPA_CLIENT_SECRET=$(kubectl get secret trustification-secret -n thoughts-app \
     -o jsonpath='{.data.oidc_client_secret}' | base64 -d)
   
   # Or set directly
   export TPA_CLIENT_SECRET=<your-client-secret>
   ```

## Usage

### Check a single package

```bash
./scripts/check_package.sh Flask 3.0.3
```

**Output if safe:**
```
✅ Package approved: Flask==3.0.3
No HIGH or CRITICAL vulnerabilities found

Add to requirements.txt:
  Flask==3.0.3  # Verified by TPA (2026-09-12)
```

**Output if vulnerable:**
```
❌ BLOCKED: Package has HIGH or CRITICAL vulnerabilities

Found vulnerabilities:
  - CVE-2024-XXXX [HIGH]: XSS vulnerability in Flask routing

🔧 Searching for safer version...
✅ Found safe version: Flask==3.0.4

Recommendation:
  Flask==3.0.4  # Auto-fixed from 3.0.3 (CVE remediation via TPA)
```

### Pre-commit hook (automated)

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Validate requirements.txt before commit

export TPA_CLIENT_SECRET=$(kubectl get secret trustification-secret -n thoughts-app \
  -o jsonpath='{.data.oidc_client_secret}' | base64 -d)

while IFS='==' read -r PACKAGE VERSION; do
  [[ "$PACKAGE" =~ ^#.*$ ]] && continue
  [[ -z "$PACKAGE" ]] && continue
  
  ./scripts/check_package.sh "$PACKAGE" "$VERSION" || exit 1
done < requirements.txt

echo "✅ All packages validated"
```

## Configuration

Edit `.tpa-config` to customize:

- `TPA_ENABLED`: Enable/disable TPA checking
- `TPA_URL`: TPA server endpoint
- `TPA_OIDC_ISSUER`: OIDC/Keycloak issuer URL
- `TPA_CLIENT_ID`: OIDC client ID

## Notes

- TPA checking only runs if `TPA_ENABLED=true` in `.tpa-config`
- Requires `jq` and `curl` installed
- Client secret must be provided via environment variable (never hardcoded)
- Script automatically suggests safer versions when vulnerabilities are found
