---
name: token-saver
description: Optimize token usage across LLM interactions. Analyze prompts for redundancy, suggest compression strategies, track token budgets, and recommend context window management techniques.
version: "1.0.0"
source: "online"
tags: [optimization, tokens, cost, efficiency, context-window]
mode: collapse
visibility: shared
permissions:
  agents: [sway, opie, outer]
  execution: "advisory-only"
---

# Token Saver

Optimize token usage and manage context window budgets.

## Capabilities

### Prompt Analysis
- Count tokens for different tokenizers (GPT, Llama, Mistral)
- Identify redundant or repetitive content
- Suggest prompt compression without meaning loss
- Estimate cost per prompt at current model pricing

### Context Window Management
- Track cumulative token usage across conversation turns
- Warn when approaching context limits
- Recommend summarization breakpoints
- Suggest context pruning strategies

### System Prompt Optimization
- Analyze system prompts for token efficiency
- Recommend condensed versions preserving intent
- Compare token costs across prompt variants
- Identify dead instructions (never triggered)

### Budget Tracking
- Per-session token accounting
- Per-agent token breakdown
- Cost estimation by model and provider
- Usage trend analysis

## Output Format

```
Token Count: <total>
Tokenizer: GPT / Llama / Mistral
Redundancy Score: Low / Medium / High
Savings Opportunity: <estimated tokens saveable>
Recommendations:
  1. <specific optimization>
  2. <specific optimization>
```

## Safety

- Advisory only — does not modify prompts
- No data exfiltration
- Token counts are estimates (model-specific)
- No autonomous prompt rewriting
