"""
Phase 3a Geometry Inspection -- READ ONLY
Loads held state from pass3_state_snapshot.json, then reports:
  1. Hub claims (top 5 by tension count)
  2. Pass-3 tension attachment (old<->new / new<->new / old<->old)
  3. Polarity analysis
  4. Summary judgment

No operators are run. Pure JSON inspection.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def load_state_from_snapshot():
    """Load state from JSON snapshot file (tries multiple fallback names)."""
    snapshot_dir = REPO_ROOT / "SovereignNEXT" / "tests"
    candidates = [
        "pass3_state_snapshot.json",
        "pass3_final_state_snapshot.json",
        "pass2_state_snapshot.json",
        "pass1_state_snapshot.json",
    ]
    for name in candidates:
        path = snapshot_dir / name
        if path.exists():
            print(f"  Loading: {path.name}")
            with open(path, encoding="utf-8") as f:
                return json.load(f)

    print(f"ERROR: No snapshot found in {snapshot_dir}")
    print("  Looked for: " + ", ".join(candidates))
    print("  Run 'python SovereignNEXT/tests/test_phase3a.py --live3' first.")
    sys.exit(1)


def classify_generation(claim_dict, all_claims_by_id):
    """Determine if a claim is orig, gen-1, gen-2, or gen-3."""
    pid = claim_dict.get("parent_id")
    if pid is None:
        return "orig"
    parent = all_claims_by_id.get(pid)
    if parent is None:
        return "gen-1?"
    if parent.get("parent_id") is None:
        return "gen-1"
    grandparent = all_claims_by_id.get(parent.get("parent_id"))
    if grandparent is None:
        return "gen-2?"
    if grandparent.get("parent_id") is None:
        return "gen-2"
    return "gen-3+"


def inspect(data):
    """Run read-only geometry inspection on raw JSON dict."""
    claims = data["claims"]
    tensions = data["tensions"]
    iteration = data.get("iteration", "?")

    all_claims_by_id = {c["id"]: c for c in claims}

    # Build tension-per-claim counts
    tension_count = defaultdict(int)
    tension_type_count = defaultdict(lambda: defaultdict(int))
    for t in tensions:
        for cid in t.get("source_claims", []):
            tension_count[cid] += 1
            tension_type_count[cid][t["relation_type"]] += 1

    print("=" * 70)
    print("PHASE 3a GEOMETRY INSPECTION -- READ ONLY")
    print(f"State: {len(claims)} claims, {len(tensions)} tensions")
    print(f"Iteration: {iteration}")
    print("=" * 70)

    # -----------------------------------------------------------------------
    # 1. HUB CLAIMS (top 5 by tension count)
    # -----------------------------------------------------------------------
    print("\n## 1. HUB CLAIMS (top 5 by total tension count)")
    print("-" * 70)

    sorted_claims = sorted(tension_count.items(), key=lambda x: -x[1])
    for rank, (cid, count) in enumerate(sorted_claims[:5], 1):
        claim = all_claims_by_id.get(cid)
        if not claim:
            continue
        gen = classify_generation(claim, all_claims_by_id)
        conf = claim.get("confidence", 0)
        types = tension_type_count[cid]
        type_str = ", ".join(f"{k}={v}" for k, v in sorted(types.items(), key=lambda x: -x[1]))
        print(f"  #{rank}  {cid} ({gen}, conf={conf:.2f})")
        print(f"       Tensions: {count} [{type_str}]")
        print(f"       Text: {claim['text'][:100]}")
        print()

    # -----------------------------------------------------------------------
    # 2. PASS-3 TENSION ATTACHMENT
    # -----------------------------------------------------------------------
    print("\n## 2. PASS-3 TENSION ATTACHMENT")
    print("-" * 70)

    # Identify pass-3 claims (the last 18 added)
    # Phase 2 = 10, Pass 1 = +24 = 34, Pass 2 = +24 = 58, Pass 3 = +18 = 76
    pass3_claim_ids = set()
    pre_pass3_claim_ids = set()

    for i, c in enumerate(claims):
        if i < 58:
            pre_pass3_claim_ids.add(c["id"])
        else:
            pass3_claim_ids.add(c["id"])

    print(f"  Pass-3 claims: {len(pass3_claim_ids)}")
    print(f"  Pre-pass-3 claims: {len(pre_pass3_claim_ids)}")

    # Identify pass-3 tensions
    pass3_tensions = []
    pre_pass3_tensions = []
    for t in tensions:
        src = t.get("source_claims", [])
        has_new = any(cid in pass3_claim_ids for cid in src)
        if has_new:
            pass3_tensions.append(t)
        else:
            pre_pass3_tensions.append(t)

    # Classify pass-3 tensions
    old_new = []
    new_new = []
    old_old = []
    for t in pass3_tensions:
        src = t.get("source_claims", [])
        new_count = sum(1 for cid in src if cid in pass3_claim_ids)
        old_count = sum(1 for cid in src if cid in pre_pass3_claim_ids)
        if new_count > 0 and old_count > 0:
            old_new.append(t)
        elif new_count >= 2:
            new_new.append(t)
        else:
            old_old.append(t)

    print(f"\n  Total tensions: {len(tensions)}")
    print(f"  Pre-pass-3 tensions: {len(pre_pass3_tensions)}")
    print(f"  Pass-3 tensions: {len(pass3_tensions)}")
    print(f"    old <-> new: {len(old_new)}")
    print(f"    new <-> new: {len(new_new)}")
    print(f"    old <-> old: {len(old_old)}")
    print()

    if old_new:
        print("  --- old <-> new tensions ---")
        for t in old_new:
            src = t.get("source_claims", [])
            new_ids = [cid for cid in src if cid in pass3_claim_ids]
            old_ids = [cid for cid in src if cid in pre_pass3_claim_ids]
            old_claim = all_claims_by_id.get(old_ids[0]) if old_ids else None
            new_claim = all_claims_by_id.get(new_ids[0]) if new_ids else None
            old_gen = classify_generation(old_claim, all_claims_by_id) if old_claim else "?"
            new_gen = classify_generation(new_claim, all_claims_by_id) if new_claim else "?"
            print(f"    {t['relation_type']}: [{old_ids[0]}({old_gen})] <-> [{new_ids[0]}({new_gen})]")
            print(f"      A: {t['pole_a'][:70]}")
            print(f"      B: {t['pole_b'][:70]}")
        print()

    if new_new:
        print("  --- new <-> new tensions ---")
        for t in new_new:
            print(f"    {t['relation_type']}: {t.get('source_claims', [])}")
            print(f"      A: {t['pole_a'][:70]}")
            print(f"      B: {t['pole_b'][:70]}")
        print()

    # Where did majority attach?
    attachment_targets = defaultdict(int)
    for t in pass3_tensions:
        for cid in t.get("source_claims", []):
            if cid in pre_pass3_claim_ids:
                attachment_targets[cid] += 1

    if attachment_targets:
        print("  --- Attachment targets (pre-pass-3 claims receiving pass-3 tensions) ---")
        for cid, cnt in sorted(attachment_targets.items(), key=lambda x: -x[1])[:8]:
            claim = all_claims_by_id.get(cid)
            gen = classify_generation(claim, all_claims_by_id) if claim else "?"
            txt = claim["text"][:70] if claim else "?"
            print(f"    {cid} ({gen}): {cnt} new tensions -- {txt}")
        print()

    # -----------------------------------------------------------------------
    # 3. POLARITY ANALYSIS
    # -----------------------------------------------------------------------
    print("\n## 3. POLARITY ANALYSIS")
    print("-" * 70)

    polarity_tensions = [t for t in tensions if t.get("relation_type") == "polarity"]
    if not polarity_tensions:
        print("  No polarity tensions detected in the current state.")
        print("  All tensions are contradiction or tradeoff type.")
    else:
        print(f"  Total polarity tensions: {len(polarity_tensions)}")
        for t in polarity_tensions:
            print(f"    {t['id']}: {t['pole_a'][:50]} <-> {t['pole_b'][:50]}")
            for cid in t.get("source_claims", []):
                other_pol = sum(1 for t2 in polarity_tensions if cid in t2.get("source_claims", []) and t2["id"] != t["id"])
                other_trd = sum(1 for t2 in tensions if t2.get("relation_type") == "tradeoff" and cid in t2.get("source_claims", []))
                if other_pol or other_trd:
                    print(f"      {cid} also in: {other_pol} other polarities, {other_trd} tradeoffs")
        print()

    # Tension type summary
    type_totals = defaultdict(int)
    for t in tensions:
        type_totals[t["relation_type"]] += 1
    print("  Tension type summary:")
    for ttype, cnt in sorted(type_totals.items(), key=lambda x: -x[1]):
        print(f"    {ttype}: {cnt}")

    # -----------------------------------------------------------------------
    # 4. SUMMARY JUDGMENT
    # -----------------------------------------------------------------------
    print("\n## 4. SUMMARY JUDGMENT")
    print("-" * 70)

    # Claims carrying most pressure
    print("\n  CONCEPTUAL PRESSURE:")
    top3 = sorted_claims[:3]
    for cid, count in top3:
        claim = all_claims_by_id.get(cid)
        gen = classify_generation(claim, all_claims_by_id) if claim else "?"
        txt = claim["text"][:80] if claim else "?"
        print(f"    {cid} ({gen}): {count} tensions -- {txt}")

    # Did pass-3 reinforce or open?
    print("\n  TENSION PATTERN:")
    reinforce_count = 0
    open_count = 0
    for t in pass3_tensions:
        src = t.get("source_claims", [])
        old_ids = [cid for cid in src if cid in pre_pass3_claim_ids]
        if old_ids:
            old_was_hub = any(tension_count[cid] > 3 for cid in old_ids)
            if old_was_hub:
                reinforce_count += 1
            else:
                open_count += 1
        else:
            open_count += 1

    total_p3 = len(pass3_tensions)
    if total_p3 > 0:
        print(f"    Reinforced existing clusters: {reinforce_count}/{total_p3} ({reinforce_count*100//total_p3}%)")
        print(f"    Opened new connections: {open_count}/{total_p3} ({open_count*100//total_p3}%)")
    else:
        print("    No pass-3 tensions to classify.")

    # Polarity structural analysis
    print("\n  POLARITY STATUS:")
    if not polarity_tensions:
        print("    No polarity tensions exist. All tension geometry is contradiction/tradeoff.")
        print("    Polarity is absent, not isolated or structural.")
    else:
        families = defaultdict(set)
        for t in polarity_tensions:
            for cid in t.get("source_claims", []):
                claim = all_claims_by_id.get(cid)
                if claim:
                    root = cid
                    current = claim
                    while current.get("parent_id") and current["parent_id"] in all_claims_by_id:
                        root = current["parent_id"]
                        current = all_claims_by_id[current["parent_id"]]
                    families[root].add(t["id"])
        cross_family = any(len(tids) > 1 for tids in families.values())
        if cross_family:
            print("    Polarity is becoming STRUCTURAL -- reinforced across multiple claim families.")
        else:
            print("    Polarity is ISOLATED -- not yet reinforced across claim families.")

    # Generation distribution
    print("\n  GENERATION DISTRIBUTION:")
    gen_counts = defaultdict(int)
    for c in claims:
        gen_counts[classify_generation(c, all_claims_by_id)] += 1
    for gen in ["orig", "gen-1", "gen-2", "gen-3+"]:
        if gen in gen_counts:
            print(f"    {gen}: {gen_counts[gen]}")

    # Confidence distribution
    print("\n  CONFIDENCE DISTRIBUTION:")
    conf_buckets = defaultdict(int)
    for c in claims:
        conf = c.get("confidence", 0)
        if conf < 0.60:
            conf_buckets["< 0.60"] += 1
        elif conf <= 0.70:
            conf_buckets["0.60-0.70"] += 1
        elif conf <= 0.85:
            conf_buckets["0.71-0.85"] += 1
        else:
            conf_buckets["0.86-1.00"] += 1
    for bucket in ["< 0.60", "0.60-0.70", "0.71-0.85", "0.86-1.00"]:
        print(f"    {bucket}: {conf_buckets.get(bucket, 0)}")

    print("\n" + "=" * 70)
    print("HOLD")
    print("=" * 70)


if __name__ == "__main__":
    print("Loading state from pass3_state_snapshot.json...")
    print("This is READ ONLY -- no operators are being run.\n")
    data = load_state_from_snapshot()
    inspect(data)
