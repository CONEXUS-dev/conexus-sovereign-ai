"""
FE Engine: Hybrid Forgetting Engine search loop.
Integrates pilot, paradox buffer, pattern mining, and operators.
"""

import hashlib
import random
import statistics
import time
from typing import List, Dict, Any, Optional

from .types import Instance, Candidate, Pattern, PilotDecision
from .evaluate import evaluate, full_repair
from .operators import apply_operator, choose_operator, apply_pattern_op, local_search_2opt
from .paradox import ParadoxBuffer
from .pattern_mining import mine_patterns
from .pilot import PilotAdapter


def derive_regime(stag: int, paradox_size: int, paradox_k: int = 5) -> str:
    """Derive steering regime from search state.

    Regime A: EXPLOIT  — stag <= 4
    Regime B: EXPLORE  — 5 <= stag <= 14
    Regime C: ESCAPE   — stag >= 15 OR (paradox full AND stag >= 10)
    """
    paradox_full = paradox_size >= paradox_k
    if stag >= 15 or (paradox_full and stag >= 10):
        return "ESCAPE"
    elif stag >= 5:
        return "EXPLORE"
    else:
        return "EXPLOIT"


def local_search_2opt_routes(inst: Instance, cand: Candidate) -> Candidate:
    """Apply 2-opt local search to each route of a candidate."""
    new_routes = []
    for route in cand.routes:
        improved = local_search_2opt(inst, route)
        new_routes.append(improved)
    # rebuild assignment from improved routes
    new_assign = list(cand.assign)
    for v, route in enumerate(new_routes):
        for c in route:
            new_assign[c] = v
    new_cand = Candidate(cid=cand.cid + "_ls", assign=new_assign)
    evaluate(inst, new_cand)
    return new_cand


def _greedy_init(inst: Instance, rng: random.Random) -> List[int]:
    """Greedy nearest-neighbour assignment."""
    assign = [0] * inst.n_customers
    remaining = list(range(inst.n_customers))
    rng.shuffle(remaining)
    vehicle_loads = [0] * inst.n_vehicles
    for c in remaining:
        # assign to vehicle with most remaining capacity that is nearest
        best_v = min(range(inst.n_vehicles),
                     key=lambda v: (vehicle_loads[v] + inst.demands[c] > inst.capacity,
                                    vehicle_loads[v]))
        assign[c] = best_v
        vehicle_loads[best_v] += inst.demands[c]
    return assign


def _random_init(inst: Instance, rng: random.Random) -> List[int]:
    """Random assignment."""
    return [rng.randint(0, inst.n_vehicles - 1) for _ in range(inst.n_customers)]


def _cluster_init(inst: Instance, rng: random.Random) -> List[int]:
    """K-means-like spatial clustering assignment."""
    centers = [inst.locations[rng.randint(0, inst.n_customers - 1)]
               for _ in range(inst.n_vehicles)]
    assign = []
    for i in range(inst.n_customers):
        loc = inst.locations[i]
        dists = [((loc[0] - c[0])**2 + (loc[1] - c[1])**2)**0.5 for c in centers]
        assign.append(dists.index(min(dists)))
    return assign


class FEEngine:
    """
    Hybrid Forgetting Engine.

    Each generation:
    1. Generate/mutate candidate pool
    2. Evaluate fitness + geometry
    3. Tag paradox-eligible candidates
    4. Update paradox buffer (k=5)
    5. Mine patterns from paradox memory
    6. Build iteration packet
    7. Query pilot for decision
    8. Apply decision: select survivors + regenerate
    9. Optional 2-opt local search every X generations
    10. Early stop if no improvement for Y generations
    """

    def __init__(self, inst: Instance, pilot: PilotAdapter,
                 seed: int = 42, pop_size: int = 20,
                 max_gens: int = 200, stagnation_limit: int = 40,
                 local_search_interval: int = 10,
                 time_limit_s: float = None,
                 pilot_every: int = 1):
        self.inst = inst
        self.pilot = pilot
        self.seed = seed
        self.pop_size = pop_size
        self.max_gens = max_gens
        self.stagnation_limit = stagnation_limit
        self.ls_interval = local_search_interval
        self.time_limit_s = time_limit_s
        self.pilot_every = max(1, pilot_every)
        self.rng = random.Random(seed)
        self.paradox = ParadoxBuffer(k=5)
        self.population: List[Candidate] = []
        self.best: Optional[Candidate] = None
        self.gen = 0
        self.stagnation = 0
        self.log: List[Dict[str, Any]] = []
        self._last_decision: Optional[PilotDecision] = None
        self._decision_cache: Dict[str, PilotDecision] = {}
        self._pilot_calls = 0
        self._cache_hits = 0
        self.pilot_call_log: List[Dict[str, Any]] = []

    def run(self) -> Dict[str, Any]:
        """Run the FE search loop. Returns results dict."""
        t0 = time.time()

        # Step 0: calibrate pilot
        self.pilot.calibrate()

        # Step 1: initialize population (mix greedy + random + cluster)
        self._init_population()

        # Main loop
        for g in range(1, self.max_gens + 1):
            self.gen = g

            # Evaluate all
            for cand in self.population:
                evaluate(self.inst, cand)

            # Sort by fitness
            self.population.sort(key=lambda c: c.fitness)

            # Update best
            if self.best is None or self.population[0].fitness < self.best.fitness:
                self.best = self.population[0]
                self.stagnation = 0
            else:
                self.stagnation += 1

            # Compute median fitness for paradox gating
            fitnesses = [c.fitness for c in self.population]
            median_f = statistics.median(fitnesses)

            # Tag and update paradox buffer
            for cand in self.population:
                self.paradox.try_add(self.inst, cand, median_f)
            self.paradox.age_all()

            # Mine patterns
            paradox_cands = self.paradox.get_candidates()
            patterns = mine_patterns(self.inst, paradox_cands) if paradox_cands else []

            # Build iteration packet
            packet = self._build_packet(median_f, patterns)
            candidate_ids = [c.cid for c in self.population]

            # Query pilot (with frequency gating + packet-hash cache)
            decision = self._get_decision(g, packet, candidate_ids)

            # Apply decision: select survivors
            survivors = self._select_survivors(decision, candidate_ids)

            # Regenerate population from survivors
            self._regenerate(survivors, decision, patterns)

            # Optional local search
            if g % self.ls_interval == 0:
                self._apply_local_search()

            # Log
            mix_short = {k: round(v, 2) for k, v in (decision.operator_mix_next or {}).items()}
            n_pops = len(decision.pattern_ops)
            regime = derive_regime(self.stagnation, self.paradox.size)
            self.log.append({
                "gen": g, "best_fitness": self.best.fitness,
                "best_distance": self.best.distance,
                "best_feasible": self.best.feasible,
                "pop_size": len(self.population),
                "paradox_size": self.paradox.size,
                "stagnation": self.stagnation,
                "operator_mix": mix_short,
                "pattern_ops_count": n_pops,
                "regime": regime,
            })

            # Progress + pilot decision summary
            if g % 20 == 0 or g == 1:
                print(f"  Gen {g:4d}: best={self.best.distance:.1f} "
                      f"feasible={self.best.feasible} stag={self.stagnation} "
                      f"paradox={self.paradox.size} "
                      f"mix={mix_short} pops={n_pops}")

            # Time limit check
            if self.time_limit_s and (time.time() - t0) >= self.time_limit_s:
                print(f"  Time limit ({self.time_limit_s}s) reached at gen {g}")
                break

            # Early stop
            if self.stagnation >= self.stagnation_limit:
                print(f"  Early stop at gen {g} (stagnation={self.stagnation})")
                break

        elapsed = time.time() - t0
        return {
            "best_distance": self.best.distance,
            "best_fitness": self.best.fitness,
            "best_feasible": self.best.feasible,
            "pilot_calls": self._pilot_calls,
            "cache_hits": self._cache_hits,
            "best_overload": self.best.overload,
            "best_routes": self.best.routes,
            "best_loads": self.best.loads,
            "generations": self.gen,
            "elapsed": elapsed,
            "paradox_summary": self.paradox.summary(),
            "pilot_call_log": self.pilot_call_log,
        }

    # ── internals ────────────────────────────────────────────────

    def _init_population(self):
        self.population = []
        inits = [_greedy_init, _random_init, _cluster_init]
        for i in range(self.pop_size):
            fn = inits[i % len(inits)]
            assign = fn(self.inst, self.rng)
            assign = full_repair(self.inst, assign, self.rng)
            cand = Candidate(cid=f"init_{i}", assign=assign)
            evaluate(self.inst, cand)
            self.population.append(cand)
        self.population.sort(key=lambda c: c.fitness)
        self.best = self.population[0]

    def _build_packet(self, median_f: float,
                      patterns: List[Pattern]) -> Dict[str, Any]:
        loads = self.best.loads
        return {
            "iteration": self.gen,
            "best_distance": round(self.best.distance, 2),
            "best_feasible": self.best.feasible,
            "route_count": sum(1 for r in self.best.routes if r),
            "loads": {
                "min": min(loads) if loads else 0,
                "max": max(loads) if loads else 0,
                "mean": round(sum(loads) / len(loads), 1) if loads else 0,
            },
            "capacity": self.inst.capacity,
            "stagnation_steps": self.stagnation,
            "paradox_size": self.paradox.size,
            "paradox_summary": self.paradox.summary(),
            "median_fitness": round(median_f, 2),
            "patterns_mined": len(patterns),
            "pattern_kinds": list(set(p.kind for p in patterns)),
            "pool_size": len(self.population),
            "candidate_ids": [c.cid for c in self.population],
        }

    @staticmethod
    def _packet_hash(packet: Dict[str, Any]) -> str:
        """Hash key fields of the packet for decision caching."""
        key_data = (
            round(packet.get("best_distance", 0), 0),
            packet.get("best_feasible"),
            packet.get("stagnation_steps", 0),
            packet.get("paradox_size", 0),
            packet.get("patterns_mined", 0),
        )
        return hashlib.md5(str(key_data).encode()).hexdigest()[:12]

    def _get_decision(self, gen: int, packet: Dict[str, Any],
                      candidate_ids: List[str]) -> PilotDecision:
        """Get pilot decision with frequency gating + packet-hash cache.

        - If gen % pilot_every != 0, reuse last decision.
        - If packet hash matches a cached decision, reuse it (cache hit).
        - Otherwise, call pilot.decide() (actual LLM/stub call).
        """
        # Frequency gate: reuse last decision on non-pilot generations
        if self._last_decision is not None and gen % self.pilot_every != 0:
            return self._last_decision

        # Packet-hash cache: skip LLM if packet barely changed
        phash = self._packet_hash(packet)
        if phash in self._decision_cache:
            self._cache_hits += 1
            self._last_decision = self._decision_cache[phash]
            return self._last_decision

        # Actual pilot call
        self._pilot_calls += 1
        decision = self.pilot.decide(packet, candidate_ids)
        self._decision_cache[phash] = decision
        self._last_decision = decision
        mix_vals = {k: round(v, 3) for k, v in (decision.operator_mix_next or {}).items()}
        pops = [op.get("op", "?") for op in decision.pattern_ops] if decision.pattern_ops else []
        stag = packet.get('stagnation_steps', 0)
        regime = derive_regime(stag, self.paradox.size)
        call_record = {
            "call_no": self._pilot_calls,
            "gen": gen,
            "stag": stag,
            "feasible": packet.get('best_feasible', False),
            "paradox_size": self.paradox.size,
            "mix": mix_vals,
            "pattern_ops": pops,
            "keep_count": len(decision.keep_ids),
            "paradox_add_count": len(decision.paradox_add_ids),
            "regime": regime,
        }
        self.pilot_call_log.append(call_record)
        print(f"  [PILOT CALL #{self._pilot_calls} gen={gen} regime={regime}] "
              f"mix={mix_vals} pops={pops} "
              f"keep={len(decision.keep_ids)} paradox_add={decision.paradox_add_ids} "
              f"stag={stag}")
        return decision

    def _select_survivors(self, decision: PilotDecision,
                          candidate_ids: List[str]) -> List[Candidate]:
        keep_set = set(decision.keep_ids)
        survivors = [c for c in self.population if c.cid in keep_set]
        # always keep the best
        if self.best not in survivors:
            survivors.insert(0, self.best)
        # ensure at least 2 survivors
        if len(survivors) < 2:
            for c in self.population:
                if c not in survivors:
                    survivors.append(c)
                if len(survivors) >= 2:
                    break
        return survivors

    @staticmethod
    def _assign_signature(assign: List[int]) -> str:
        """Hash route structure for duplicate detection."""
        return ",".join(str(v) for v in assign)

    def _deduplicate(self, pop: List[Candidate]) -> List[Candidate]:
        """Remove exact-duplicate assignments, keeping first occurrence."""
        seen = set()
        unique = []
        for c in pop:
            sig = self._assign_signature(c.assign)
            if sig not in seen:
                seen.add(sig)
                unique.append(c)
        return unique

    def _inject_fresh(self, count: int) -> List[Candidate]:
        """Inject fresh random/greedy candidates for diversity."""
        inits = [_greedy_init, _random_init, _cluster_init]
        fresh = []
        for i in range(count):
            fn = inits[i % len(inits)]
            assign = fn(self.inst, self.rng)
            assign = full_repair(self.inst, assign, self.rng)
            cand = Candidate(cid=f"g{self.gen}_fresh{i}", assign=assign)
            evaluate(self.inst, cand)
            fresh.append(cand)
        return fresh

    def _regenerate(self, survivors: List[Candidate],
                    decision: PilotDecision,
                    patterns: List[Pattern]):
        """Fill population from survivors using mutation + pattern injection."""
        new_pop = list(survivors)
        mix = decision.operator_mix_next
        if not mix:
            mix = {"swap": 0.3, "relocate": 0.35, "reverse": 0.15, "cross_exchange": 0.2}

        # Apply pattern ops from pilot decision
        pattern_assigns = []
        for pop_entry in decision.pattern_ops:
            op_name = pop_entry.get("op", "")
            custs = pop_entry.get("customers", [])
            pat = Pattern(kind=op_name, customers=custs, score=0)
            parent = self.rng.choice(survivors)
            try:
                new_assign = apply_pattern_op(op_name, self.inst, parent.assign, pat, self.rng)
                new_assign = full_repair(self.inst, new_assign, self.rng)
                pattern_assigns.append(new_assign)
            except Exception:
                pass

        for idx, assign in enumerate(pattern_assigns):
            cand = Candidate(cid=f"g{self.gen}_pat{idx}", assign=assign)
            evaluate(self.inst, cand)
            new_pop.append(cand)

        # Fill rest with mutation
        counter = 0
        while len(new_pop) < self.pop_size:
            parent = self.rng.choice(survivors)
            op_name = choose_operator(mix, self.rng)
            new_assign = apply_operator(op_name, self.inst, parent.assign, self.rng)
            new_assign = full_repair(self.inst, new_assign, self.rng)
            cand = Candidate(cid=f"g{self.gen}_m{counter}", assign=new_assign)
            evaluate(self.inst, cand)
            new_pop.append(cand)
            counter += 1

        # Duplicate suppression: if >50% duplicates, inject fresh
        unique = self._deduplicate(new_pop)
        if len(unique) < len(new_pop) * 0.5:
            fresh_count = self.pop_size - len(unique)
            unique.extend(self._inject_fresh(fresh_count))
        self.population = unique[:self.pop_size] if len(unique) > self.pop_size else unique

    def _apply_local_search(self):
        """Apply 2-opt to top candidates."""
        for i in range(min(3, len(self.population))):
            cand = self.population[i]
            improved = local_search_2opt_routes(self.inst, cand)
            if improved.fitness < cand.fitness:
                self.population[i] = improved
                if improved.fitness < self.best.fitness:
                    self.best = improved
