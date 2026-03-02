# Extensions Needed for Production

This document outlines the extensions needed to make the Hybrid FE VRP system production-ready.

## 1. LLM Integration (CRITICAL)

**Status:** Placeholder implemented  
**Priority:** HIGH  
**File:** `pilot_adapter.py`

### What's Needed:
Replace `llm_chat_call_placeholder()` with your actual LLM provider:

```python
def llm_chat_call_placeholder(messages: List[Dict[str, str]]) -> str:
    """
    Example implementations:
    
    # OpenAI:
    import openai
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content
    
    # Anthropic:
    import anthropic
    client = anthropic.Anthropic(api_key="...")
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        messages=messages
    )
    return message.content[0].text
    
    # Local Model (Ollama, LM Studio, etc.):
    import requests
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={"model": "llama2", "messages": messages}
    )
    return response.json()["message"]["content"]
    """
    raise NotImplementedError("Implement with your LLM provider")
```

### Testing:
Once implemented, test calibration:
```python
from pilot_adapter import PilotAdapter, llm_chat_call_placeholder

pilot = PilotAdapter(mode="llm", llm_chat_fn=llm_chat_call_placeholder)
pilot.calibrate()  # Should complete CONEXUS-STEEL-04 protocol
```

---

## 2. Pattern Mining from Paradox Buffer

**Status:** Not implemented  
**Priority:** MEDIUM  
**File:** `fe_hybrid_vrp.py`

### What's Needed:
Implement pattern detection functions:

```python
def mine_tight_pairs(paradox_buffer: List[Candidate]) -> List[Tuple[int, int]]:
    """
    Detect customer pairs that frequently appear close together
    in paradox buffer solutions.
    
    Returns: List of (customer_id_1, customer_id_2) pairs
    """
    pass

def mine_clusters(paradox_buffer: List[Candidate]) -> List[List[int]]:
    """
    Detect customer clusters that appear together across
    multiple paradox buffer solutions.
    
    Returns: List of customer clusters
    """
    pass

def mine_depot_leg_culprits(paradox_buffer: List[Candidate]) -> List[int]:
    """
    Identify customers that consistently create long depot legs.
    
    Returns: List of customer IDs
    """
    pass
```

### Integration:
Add to `build_iteration_packet()`:
```python
pattern_hints = {
    "tight_pairs": mine_tight_pairs(paradox_buffer),
    "cluster_candidates": mine_clusters(paradox_buffer),
    "depot_leg_culprits": mine_depot_leg_culprits(paradox_buffer)
}
```

---

## 3. Enhanced Logging (JSONL Format)

**Status:** Basic logging implemented  
**Priority:** MEDIUM  
**File:** `fe_hybrid_vrp.py`

### What's Needed:
Add detailed JSONL iteration logs:

```python
def log_iteration(g, candidates, decision, paradox_buffer, best_seen):
    """Write detailed iteration log to JSONL file."""
    log_entry = {
        "g": g,
        "timestamp": time.time(),
        "best_in_pool": {"f": min(c.f for c in candidates), ...},
        "best_seen": {"f": best_seen.f, ...},
        "diversity": {
            "avg_hamming": ...,
            "min_hamming_prev": ...
        },
        "paradox_buffer": [{"id": b.cid, "f": b.f} for b in paradox_buffer],
        "pilot_decision": {
            "kept_count": len(decision["keep_ids"]),
            "paradox_adds": len(decision["paradox_add_ids"]),
            "pattern_ops": decision["pattern_ops"]
        },
        "proto_moments": decision["proto"]["moments"]
    }
    
    with open("run_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

---

## 4. Scaling Test Suite

**Status:** Not implemented  
**Priority:** HIGH  
**File:** New file `scaling_tests.py`

### What's Needed:
Test complexity advantage hypothesis:

```python
def run_scaling_suite():
    """
    Run on multiple instance sizes to validate:
    "Improvement over baseline increases as problem complexity increases"
    """
    sizes = [50, 100, 200, 400, 800]
    results = []
    
    for n in sizes:
        instance = generate_vrp_instance(n_customers=n, n_vehicles=max(5, n//40))
        
        baseline_result = run_baseline(instance)
        fe_result = run_fe_hybrid(instance, max_iters=100)
        
        gain_pct = ((baseline_result.f - fe_result.f) / baseline_result.f) * 100
        
        results.append({
            "n_customers": n,
            "complexity_index": calculate_complexity_index(instance),
            "gain_pct": gain_pct
        })
    
    # Plot gain_pct vs complexity_index
    # Should show upward trend
    plot_scaling_results(results)
```

---

## 5. Visualization Tools

**Status:** Not implemented  
**Priority:** LOW  
**File:** New file `visualize.py`

### What's Needed:

```python
def plot_routes(solution, title="VRP Solution"):
    """Plot vehicle routes on 2D map."""
    pass

def plot_convergence(logs, title="Convergence"):
    """Plot best_f over iterations."""
    pass

def plot_paradox_buffer_evolution(logs):
    """Show how paradox buffer changes over time."""
    pass

def plot_diversity_trends(logs):
    """Plot hamming distance trends."""
    pass
```

---

## 6. Real-World Instance Loader

**Status:** Not implemented  
**Priority:** MEDIUM  
**File:** New file `instance_loader.py`

### What's Needed:
Load standard VRP benchmark instances:

```python
def load_solomon_instance(filename: str) -> Dict[str, Any]:
    """Load Solomon benchmark instance (C101, R101, RC101, etc.)."""
    pass

def load_gehring_homberger_instance(filename: str) -> Dict[str, Any]:
    """Load Gehring & Homberger large instance."""
    pass

def load_custom_csv(filename: str) -> Dict[str, Any]:
    """Load custom CSV format: customer_id, x, y, demand."""
    pass
```

---

## 7. Advanced Pattern Operations

**Status:** Basic implementations only  
**Priority:** LOW  
**File:** `fe_hybrid_vrp.py`

### What's Needed:
Enhance pattern injection operations:

```python
def apply_spine_split(assign, customers, rng):
    """
    Split a chain of customers across two vehicles
    while maintaining adjacency.
    """
    pass

def apply_cluster_lock_smart(assign, customers, rng):
    """
    Lock cluster to vehicle with best centroid proximity.
    """
    pass
```

---

## 8. Calibration Persistence

**Status:** Not implemented  
**Priority:** LOW  
**File:** `pilot_adapter.py`

### What's Needed:
Cache calibration state:

```python
def save_calibration(pilot: PilotAdapter, filepath: str):
    """Save calibration state to disk."""
    pass

def load_calibration(filepath: str) -> PilotAdapter:
    """Load pre-calibrated pilot from disk."""
    pass
```

This avoids re-running the 9-Gear protocol for every run.

---

## 9. Multi-Run Statistics

**Status:** Not implemented  
**Priority:** MEDIUM  
**File:** New file `statistical_validation.py`

### What's Needed:
Run multiple seeds and compute statistics:

```python
def run_statistical_validation(n_runs=10):
    """
    Run FE vs baseline multiple times with different seeds.
    Compute mean, std, confidence intervals.
    """
    results = []
    for seed in range(n_runs):
        baseline = run_baseline(seed=seed)
        fe = run_fe_hybrid(seed=seed)
        results.append({
            "seed": seed,
            "baseline_f": baseline.f,
            "fe_f": fe.f,
            "improvement": (baseline.f - fe.f) / baseline.f
        })
    
    # Statistical analysis
    mean_improvement = np.mean([r["improvement"] for r in results])
    std_improvement = np.std([r["improvement"] for r in results])
    
    # t-test for significance
    from scipy import stats
    t_stat, p_value = stats.ttest_rel(
        [r["baseline_f"] for r in results],
        [r["fe_f"] for r in results]
    )
    
    return {
        "mean_improvement": mean_improvement,
        "std_improvement": std_improvement,
        "p_value": p_value,
        "significant": p_value < 0.05
    }
```

---

## 10. Error Handling & Recovery

**Status:** Basic fallback implemented  
**Priority:** MEDIUM  
**File:** `pilot_adapter.py`, `fe_hybrid_vrp.py`

### What's Needed:
Enhanced error recovery:

```python
# In pilot_adapter.py:
- Retry logic for LLM failures (with exponential backoff)
- Partial decision recovery (use what's valid, fill rest with fallback)
- Calibration checkpointing (resume from last successful gear)

# In fe_hybrid_vrp.py:
- Handle OR-Tools solver failures gracefully
- Detect and recover from population collapse
- Automatic parameter adjustment on stagnation
```

---

## Priority Summary

### Immediate (Required for Production):
1. **LLM Integration** - Without this, only stub mode works
4. **Scaling Test Suite** - Needed to validate core hypothesis

### Important (Enhances Performance):
2. **Pattern Mining** - Improves pilot decision quality
3. **Enhanced Logging** - Essential for debugging and analysis
6. **Real-World Instances** - Test on actual benchmark problems

### Nice to Have (Improves Usability):
5. **Visualization Tools** - Helps understand system behavior
8. **Calibration Persistence** - Saves time on repeated runs
9. **Multi-Run Statistics** - Validates statistical significance
10. **Error Handling** - Makes system more robust

### Optional (Future Work):
7. **Advanced Pattern Operations** - Incremental improvements

---

## Testing Checklist

Before considering the system production-ready:

- [ ] LLM integration tested with calibration
- [ ] Validation harness runs successfully with all 3 modes
- [ ] Scaling tests show upward trend in gain% vs complexity
- [ ] Pattern mining produces useful hints
- [ ] Logs are detailed enough for post-run analysis
- [ ] System handles OR-Tools failures gracefully
- [ ] Multi-run statistics show significant improvement
- [ ] Real-world instances (Solomon, etc.) tested
- [ ] Documentation is complete and accurate

---

## Current Status

**What Works Now:**
✅ Core FE engine with paradox buffer  
✅ OR-Tools TSP integration  
✅ Stub pilot (deterministic mode)  
✅ CONEXUS-STEEL-04 calibration gate  
✅ Basic validation harness  
✅ Pattern operation framework  

**What Needs Work:**
⚠️ LLM integration (placeholder only)  
⚠️ Pattern mining (not implemented)  
⚠️ Detailed logging (basic only)  
⚠️ Scaling tests (not implemented)  
⚠️ Visualization (not implemented)  

**Estimated Time to Production:**
- With LLM integration: 2-4 hours
- With all high-priority items: 1-2 days
- With all items: 3-5 days
