"""
Core data types for FE-VRP Optimizer.
Canonical indexing: customers 0..N-1, depot is separate.
"""

import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple


@dataclass
class Instance:
    """VRP problem instance. Customers indexed 0..N-1."""
    name: str
    n_customers: int
    n_vehicles: int
    capacity: int
    depot: Tuple[float, float]
    locations: List[Tuple[float, float]]   # length N, indexed 0..N-1
    demands: List[int]                      # length N, indexed 0..N-1
    seed: int

    @property
    def total_demand(self) -> int:
        return sum(self.demands)

    @property
    def total_capacity(self) -> int:
        return self.n_vehicles * self.capacity

    @property
    def is_feasible(self) -> bool:
        return self.total_capacity >= self.total_demand

    def dist(self, i: int, j: int) -> float:
        """Euclidean distance. Use -1 for depot."""
        a = self.depot if i == -1 else self.locations[i]
        b = self.depot if j == -1 else self.locations[j]
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "n_customers": self.n_customers,
            "n_vehicles": self.n_vehicles,
            "capacity": self.capacity,
            "depot": list(self.depot),
            "locations": [list(loc) for loc in self.locations],
            "demands": self.demands,
            "seed": self.seed,
            "total_demand": self.total_demand,
            "total_capacity": self.total_capacity,
            "is_feasible": self.is_feasible,
        }

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "Instance":
        with open(path) as f:
            d = json.load(f)
        return cls(
            name=d["name"], n_customers=d["n_customers"],
            n_vehicles=d["n_vehicles"], capacity=d["capacity"],
            depot=tuple(d["depot"]),
            locations=[tuple(loc) for loc in d["locations"]],
            demands=d["demands"], seed=d["seed"],
        )


@dataclass
class Candidate:
    """A VRP solution candidate."""
    cid: str
    assign: List[int]                       # length N, assign[i] = vehicle
    routes: List[List[int]] = field(default_factory=list)
    distance: float = 0.0
    loads: List[int] = field(default_factory=list)
    overload: int = 0
    fitness: float = 0.0                    # distance + penalty * overload
    feasible: bool = False
    metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "cid": self.cid, "assign": self.assign,
            "routes": self.routes, "distance": self.distance,
            "loads": self.loads, "overload": self.overload,
            "fitness": self.fitness, "feasible": self.feasible,
            "metrics": self.metrics,
        }


@dataclass
class ParadoxEntry:
    """An entry in the paradox buffer."""
    candidate: Candidate
    score: float = 0.0          # informativeness score
    age: int = 0                # generations since added
    patterns_mined: int = 0     # how many times patterns were extracted


@dataclass
class Pattern:
    """A pattern mined from paradox buffer."""
    kind: str                   # CLUSTER, SPINE, DEPOT_LEG
    customers: List[int]        # customer indices involved
    score: float = 0.0
    source_cid: str = ""


# --- Pilot decision types ---

ALLOWED_ACTIONS = {
    "APPLY_OPERATOR", "FOCUS_ROUTE", "REPAIR_CAPACITY",
    "DIVERSIFY", "INTENSIFY", "STOP",
}
ALLOWED_OPERATORS = {"swap", "relocate", "reverse", "cross_exchange"}
ALLOWED_PATTERN_OPS = {"CLUSTER_LOCK", "SPINE_SPLIT", "CAPACITY_REPAIR", "DEPOT_LEG_MIN"}
ALLOWED_MOMENT_TYPES = {
    "THRESHOLD_SHIFT", "PARADOX_COMPETITIVE", "NEW_PATTERN", "DIVERSITY_PULSE",
}

REQUIRED_DECISION_KEYS = {
    "keep_ids", "paradox_add_ids", "operator_mix_next",
    "pattern_ops", "proto", "rationale",
}


@dataclass
class PilotDecision:
    """Strict JSON decision from pilot."""
    keep_ids: List[str] = field(default_factory=list)
    paradox_add_ids: List[str] = field(default_factory=list)
    operator_mix_next: Dict[str, float] = field(default_factory=dict)
    pattern_ops: List[Dict[str, Any]] = field(default_factory=list)
    proto: Dict[str, Any] = field(default_factory=lambda: {"moments": []})
    rationale: Dict[str, str] = field(default_factory=lambda: {
        "survival_logic": "", "paradox_logic": ""
    })

    def to_dict(self) -> dict:
        return {
            "keep_ids": self.keep_ids,
            "paradox_add_ids": self.paradox_add_ids,
            "operator_mix_next": self.operator_mix_next,
            "pattern_ops": self.pattern_ops,
            "proto": self.proto,
            "rationale": self.rationale,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, d: dict) -> "PilotDecision":
        return cls(
            keep_ids=d.get("keep_ids", []),
            paradox_add_ids=d.get("paradox_add_ids", []),
            operator_mix_next=d.get("operator_mix_next", {}),
            pattern_ops=d.get("pattern_ops", []),
            proto=d.get("proto", {"moments": []}),
            rationale=d.get("rationale", {"survival_logic": "", "paradox_logic": ""}),
        )
