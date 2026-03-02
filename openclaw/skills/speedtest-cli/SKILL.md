---
name: speedtest-cli
description: Test network speed, latency, and connectivity. Measure download/upload speeds, ping to common endpoints, and diagnose network issues affecting API calls and model downloads.
version: "1.0.0"
source: "online"
tags: [network, speed, latency, diagnostics, utility]
mode: collapse
visibility: shared
permissions:
  agents: [sway, outer]
  execution: "governed"
requires:
  bins: [python3]
  packages: [speedtest-cli]
---

# Speedtest CLI

Test network speed and diagnose connectivity issues.

## Capabilities

### Speed Testing
- Download speed measurement (Mbps)
- Upload speed measurement (Mbps)
- Ping / latency measurement (ms)
- Jitter measurement (ms)
- Server selection (nearest or specified)

### Connectivity Diagnostics
- Test reachability to common endpoints (GitHub, HuggingFace, PyPI, Ollama)
- DNS resolution timing
- SSL/TLS handshake timing
- Route tracing for slow connections

### API Endpoint Testing
- Test latency to CONEXUS Gateway
- Test latency to Qdrant instance
- Test latency to Ollama API
- Measure response times for health endpoints

### Reporting
- Single-run summary
- Comparison against baseline
- Historical trend (if stored)

## Usage

```bash
# Basic speed test
python -m speedtest

# Test specific endpoint
python scripts/ping_test.py --target localhost:8002

# Full diagnostics
python scripts/network_diag.py --all
```

## Output Format

```
Speed Test Results:
  Download: <Mbps>
  Upload: <Mbps>
  Ping: <ms>
  Jitter: <ms>
  Server: <location>

Endpoint Latency:
  Gateway (localhost:8002): <ms>
  Qdrant (localhost:6333): <ms>
  Ollama (localhost:11434): <ms>
```

## Safety

- Read-only network testing
- No data transmission beyond speed test packets
- No modification of network configuration
- Results stored locally only
