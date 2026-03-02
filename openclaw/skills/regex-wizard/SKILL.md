---
name: regex-wizard
description: Build, test, explain, and debug regular expressions. Supports Python, JavaScript, and PCRE flavors. Generates patterns from natural language descriptions and validates against test strings.
version: "1.0.0"
source: "online"
tags: [regex, patterns, validation, text-processing, utility]
mode: collapse
visibility: shared
permissions:
  agents: [sway, opie, outer]
  execution: "advisory-only"
---

# Regex Wizard

Build and debug regular expressions from natural language descriptions.

## Capabilities

### Pattern Generation
- Convert natural language to regex: "match email addresses" → `[\w.-]+@[\w.-]+\.\w+`
- Support Python (`re`), JavaScript, and PCRE flavors
- Generate named capture groups when appropriate

### Pattern Explanation
- Break down complex regex into plain English
- Identify potential issues (greedy vs lazy, catastrophic backtracking)
- Show match groups and their purposes

### Testing & Validation
- Test patterns against provided sample strings
- Show matches, groups, and positions
- Identify edge cases that may fail

### Debugging
- Analyze why a pattern fails on specific input
- Suggest fixes with explanations
- Warn about common pitfalls (anchoring, escaping, character classes)

## Output Format

```
Pattern: <regex>
Flavor: Python / JavaScript / PCRE
Explanation: <plain English breakdown>
Matches: <test results>
Edge cases: <potential failures>
```

## Safety

- Advisory only — does not execute code
- No file system access
- No network access
- Patterns are generated, not executed
