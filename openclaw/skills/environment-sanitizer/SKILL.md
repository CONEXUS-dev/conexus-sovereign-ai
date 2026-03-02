---
name: environment-sanitizer
description: Audit and sanitize environment variables, .env files, and configuration for security. Detect exposed secrets, validate required variables, and ensure safe deployment configuration.
version: "1.0.0"
source: "online"
tags: [security, environment, secrets, configuration, audit]
mode: collapse
visibility: core
permissions:
  agents: [sway, outer]
  execution: "advisory-only"
---

# Environment Sanitizer

Audit environment variables and configuration for security issues.

## Capabilities

### Secret Detection
- Scan `.env` files for exposed API keys, tokens, and passwords
- Detect hardcoded secrets in source files
- Identify secrets in git history (committed credentials)
- Flag high-entropy strings that may be secrets

### Variable Validation
- Check required environment variables are set
- Validate variable formats (URLs, paths, tokens)
- Detect conflicting or duplicate variables
- Warn about unused variables

### Configuration Audit
- Compare `.env` against `.env.example` for missing variables
- Verify file permissions on sensitive configs
- Check `.gitignore` includes all secret files
- Validate deployment configuration completeness

### Sanitization Recommendations
- Suggest rotation for exposed credentials
- Recommend secret management solutions (vault, KMS)
- Generate safe `.env.example` templates
- Provide remediation steps per finding

## Output Format

```
Scan Results:
  Files scanned: <count>
  Secrets found: <count>
  Warnings: <count>

Findings:
  [CRITICAL] <file>:<line> — Exposed API key: <masked>
  [WARNING] <file>:<line> — Missing from .gitignore
  [INFO] <variable> — Not set but referenced

Recommendations:
  1. <specific action>
  2. <specific action>
```

## Safety

- Advisory only — does not modify files
- Secrets are masked in all output (first 4 chars only)
- No external transmission of discovered secrets
- All findings logged locally for review
