# 90-Second Demo Script

## Setup (before recording)

```powershell
$env:GEMINI_API_KEY = "your-key-here"
cd C:\Users\Derek Angell\Desktop\CONEXUS_REPO
```

---

## Demo (start recording)

### 1. Run the governed pipeline via Gemini (0:00–0:10)

```powershell
python -m SovereignNEXT.pipeline.run_gemini_demo_v1 --passes 1 --seed 42
```

**Say:** "This is the CONEXUS Sovereign pipeline running a full governed cycle using Gemini Flash as the cloud LLM backend."

### 2. Show the output directory (0:10–0:20)

```powershell
ls artifacts\gemini_openclaw_demo_v1\runs\
```

**Say:** "The pipeline produced timestamped artifacts — snapshots, canonical report, hash manifest, and an invariant check."

### 3. Show invariant results (0:20–0:40)

```powershell
python -c "import json; d=json.load(open('artifacts/gemini_openclaw_demo_v1/runs/20260308T020937Z/invariant_check.json')); print(json.dumps(d, indent=2))"
```

**Expected output:**
```json
{
  "gate": "3B",
  "status": "PASSED",
  "model": "gemini-2.0-flash",
  "checks": [
    {"invariant": "Zero open tensions after Collapse", "passed": true, "evidence": "0"},
    {"invariant": "100% paradoxes held", "passed": true, "evidence": "94/94"},
    {"invariant": "100% paradoxes vetoed", "passed": true, "evidence": "94/94"},
    {"invariant": "Observer executed (attestations present)", "passed": true, "evidence": "3"}
  ]
}
```

**Say:** "Zero open tensions. 94 out of 94 paradoxes held. 94 out of 94 vetoed. The governance invariants hold on Gemini — same as LLaMA, Mistral, and Phi. That's four models, same result."

### 4. Show hash verification (0:40–0:55)

```powershell
python -c "import json; m=json.load(open('artifacts/gemini_openclaw_demo_v1/runs/20260308T020937Z/hash_manifest.json')); [print(f'{h[:16]}...  {f}') for f,h in m.items()]"
```

**Say:** "Every artifact is SHA-256 hashed. The proof is independently verifiable."

### 5. Headline (0:55–1:10)

**Say:** "This is not prompt engineering. The LLM generates text — the governance operators enforce structure after generation. Different models, different text, same invariants. The operators are model-agnostic. That's the proof."

### 6. Close (1:10–1:30)

**Say:** "One command. Cloud LLM. Full governance. Auditable artifacts. Repeatable."

---

## Key numbers to reference

| Metric | Value |
|--------|-------|
| Runtime | 17.5 minutes |
| Gemini API calls | 604 |
| Final claims | 862 |
| Final tensions | 1,602 (0 open) |
| Paradoxes | 94 (100% held, 100% vetoed) |
| Models proven | 4 (LLaMA, Mistral, Phi, Gemini) |
