---
name: model-usage-tracker
description: Track per-model usage costs, token consumption, and performance metrics. Summarize usage by model, provider, and time period. Supports local LLM and cloud API tracking.
version: "1.0.0"
source: "openclaw/skills (steipete/model-usage)"
tags: [monitoring, cost, usage, metrics, models]
mode: dual
visibility: shared
permissions:
  agents: [sway, opie, outer]
  execution: "governed"
---

# Model Usage Tracker

Track and summarize per-model usage costs and performance metrics.

## Capabilities

### Usage Tracking
- Per-model token consumption (input + output)
- Per-model inference time
- Per-model cost estimation
- Session and cumulative totals

### Provider Support
- Local models: Phi-4-mini (llama-cpp-python), Llama-3 8B (GPT4All), Mistral 7B (GPT4All)
- Cloud APIs: OpenAI, Anthropic, Google (when configured)
- Ollama instances

### Reporting
- Current model usage (most recent session)
- All models summary (historical)
- Cost breakdown by provider
- Performance comparison (latency, throughput)

### Output Formats
- Text summary (default)
- JSON (for programmatic use)
- Markdown table (for reports)

## Usage

```bash
# Current model usage
python scripts/model_usage.py --mode current

# All models summary
python scripts/model_usage.py --mode all

# JSON output
python scripts/model_usage.py --mode all --format json --pretty
```

## Tracked Metrics

| Metric | Description |
|--------|-------------|
| tokens_in | Input tokens consumed |
| tokens_out | Output tokens generated |
| latency_ms | Inference time per request |
| cost_usd | Estimated cost (cloud only) |
| requests | Total request count |
| errors | Failed request count |

## Safety

- Read-only metrics collection
- No model modification
- No external data transmission
- All metrics stored locally
