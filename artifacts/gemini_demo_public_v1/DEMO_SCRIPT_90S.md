# Demo Script — 90 Seconds

A step-by-step script for recording a screen capture of the CONEXUS Sovereign Gemini demo.

---

## Before Recording

```bash
export GEMINI_API_KEY="your-key-here"              # Linux/Mac
$env:GEMINI_API_KEY = "your-key-here"               # PowerShell
```

Ensure you are in the repository root directory.

---

## Steps

### Step 1: Run the governed pipeline (0:00)

```bash
python -m SovereignNEXT.pipeline.run_gemini_demo_v1 --passes 1 --seed 42
```

The pipeline loads the sealed V5 baseline, runs one Become pass via Gemini Flash, then applies governance operators: Collapse → Become → Paradox-Hold → Observer.

Runtime: 15–25 minutes. The demo script assumes this has already completed and you are showing the results.

### Step 2: Show output directory (0:00–0:10)

```bash
ls artifacts/gemini_openclaw_demo_v1/runs/
```

A timestamped folder appears containing: state snapshots, canonical report, run metadata, hash manifest, and invariant check.

### Step 3: Show invariant results (0:10–0:30)

```bash
python -c "import json; print(json.dumps(json.load(open('artifacts/gemini_demo_public_v1/run_artifacts/invariant_check.json')), indent=2))"
```

Expected output:

```
Gate 3B: PASSED
  Zero open tensions after Collapse: 0
  100% paradoxes held: 94/94
  100% paradoxes vetoed: 94/94
  Observer executed: 3 attestations
```

Talking point: "Zero open tensions. 94 out of 94 paradoxes held. 94 out of 94 vetoed. The governance invariants hold on Gemini — the same result as LLaMA, Mistral, and Phi. Four models, same structural outcome."

### Step 4: Verify artifact hashes (0:30–0:45)

```bash
python artifacts/gemini_demo_public_v1/verification/_verify.py
```

Expected output: `VERIFIED — all hashes match`.

Talking point: "Every artifact is SHA-256 hashed. The proof is independently verifiable."

### Step 5: Show run metadata (0:45–0:55)

```bash
python -c "import json; d=json.load(open('artifacts/gemini_demo_public_v1/run_artifacts/run_metadata.json')); print(f'Model: {d[\"model\"]}'); print(f'Duration: {d[\"duration_sec\"]:.0f}s'); print(f'Claims: {d[\"final_claims\"]}'); print(f'Tensions: {d[\"final_tensions\"]}'); print(f'Paradoxes: {d[\"final_paradoxes\"]}')"
```

### Step 6: Headline (0:55–1:10)

Talking point: "The LLM generates text. The governance operators enforce structure after generation. Different models produce different text, but the invariants are identical. The operators are model-agnostic. That is the proof."

### Step 7: Close (1:10–1:30)

Talking point: "One command. Cloud LLM. Full governance. Auditable artifacts. Repeatable."

---

## Reproducibility Note

Running the same command with `--seed 42` will produce the same governance outcomes (zero open tensions, 100% held, 100% vetoed). Text content will vary due to LLM non-determinism, but structural invariants are stable.

---

## Key Numbers

| Metric | Value |
|--------|-------|
| Runtime | 17.5 minutes |
| Gemini API calls | 604 |
| Final claims | 862 |
| Final tensions | 1,602 (0 open) |
| Paradoxes | 94 (100% held, 100% vetoed) |
| Models confirmed | 4 (LLaMA, Mistral, Phi, Gemini) |
