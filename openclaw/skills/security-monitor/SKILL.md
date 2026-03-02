---
name: security-monitor
description: Proactive security monitoring for OpenClaw deployments. Detects supply chain attacks, memory poisoning, credential exfiltration, SKILL.md injection, and WebSocket hijacking. Real-time threat scanning.
version: "1.0.0"
source: "adibirzu/openclaw-security-monitor"
tags: [security, monitoring, threats, scanning, defense]
mode: dual
visibility: core
permissions:
  agents: [sway, outer]
  execution: "governed"
---

# Security Monitor

Proactive security monitoring for OpenClaw and CONEXUS deployments.

## Capabilities

### Threat Scanning
- 32-point security scan covering:
  - C2 infrastructure detection
  - Credential exfiltration patterns
  - Memory poisoning attempts
  - SKILL.md injection vectors
  - WebSocket hijacking
  - Reverse shell detection
  - Supply chain attack indicators

### Continuous Monitoring
- Periodic security scans (configurable interval)
- Real-time alert on threat detection
- Severity classification: info / warning / critical / emergency

### Remediation Guidance
- Specific fix recommendations per threat
- Rollback procedures for compromised skills
- Quarantine protocols for suspicious components

### Audit Trail
- All scans logged with timestamps
- Threat history maintained
- False positive tracking
- Compliance reporting

## Commands

- `/security-scan` — Run full security scan
- `/security-dashboard` — View threat summary
- `/security-network` — Scan network connections
- `/security-remediate` — Get fix recommendations

## Safety

- Read-only scanning — no system modification
- All findings reported to Derek for action
- No autonomous remediation without approval
- Scan results stored locally only
