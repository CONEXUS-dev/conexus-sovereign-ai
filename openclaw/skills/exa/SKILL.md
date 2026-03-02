---
name: exa
description: Neural web search and code context via Exa AI API. Search people, companies, news, research, code. Requires EXA_API_KEY.
version: "1.0.0"
source: "openclaw/skills (fardeenxyz/exa)"
tags: [search, web, neural, research, api]
mode: dual
visibility: shared
permissions:
  agents: [sway, opie, outer]
  execution: "governed"
requires:
  env: [EXA_API_KEY]
---

# Exa — Neural Web Search

Direct API access to Exa's neural search engine for finding documentation, code examples, research papers, and company information.

## Setup

1. Get your API Key from [Exa Dashboard](https://dashboard.exa.ai/api-keys)
2. Set in environment:
```bash
export EXA_API_KEY="your-key-here"
```

## Capabilities

### Web Search
- Neural search (semantic understanding)
- Fast search (keyword-optimized)
- Deep search (comprehensive)
- Category filters: company, research-paper, news, github, tweet, personal-site, pdf

### Code Context
- Find relevant code snippets and documentation
- Search by concept, not just keywords

### Content Extraction
- Extract full text from URLs
- Clean content for downstream processing

## Usage

```bash
# Basic search
bash scripts/search.sh "AI agents 2024" [num_results] [type]

# Code context
bash scripts/code.sh "query" [num_results]

# Extract content from URLs
bash scripts/content.sh "url1" "url2"
```

## Safety

- Read-only: no data modification
- API key required for all operations
- Rate-limited by Exa's API policies
- No autonomous execution — results returned for agent processing
