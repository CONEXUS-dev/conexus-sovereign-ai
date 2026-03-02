"""
Candidate - VRP solution representation with canonical 0..N-1 indexing
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Candidate:
    """
    VRP solution candidate.
    
    Indexing:
    - assignment[i] = vehicle_id for customer i (i in 0..N-1)
    - routes[v] = list of customer indices for vehicle v
    - All customer indices are 0..N-1
    """
    
    id: str
    assignment: List[int]  # Length N, assignment[i] = vehicle for customer i
    routes: List[List[int]] = field(default_factory=list)  # routes[v] = customer list
    distance: float = 0.0
    loads: List[int] = field(default_factory=list)  # loads[v] = total demand on vehicle v
    overload: int = 0  # Total capacity violation
    objective: float = 0.0  # Final objective (distance + penalties)
    
    # Metadata
    feasible: bool = True
    coverage_valid: bool = True
    conservation_valid: bool = True
    capacity_valid: bool = True
    
    # Metrics for pilot
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'assignment': self.assignment,
            'routes': self.routes,
            'distance': self.distance,
            'loads': self.loads,
            'overload': self.overload,
            'objective': self.objective,
            'feasible': self.feasible,
            'coverage_valid': self.coverage_valid,
            'conservation_valid': self.conservation_valid,
            'capacity_valid': self.capacity_valid,
            'metrics': self.metrics
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Candidate':
        """Create candidate from dictionary."""
        return cls(
            id=data['id'],
            assignment=data['assignment'],
            routes=data.get('routes', []),
            distance=data.get('distance', 0.0),
            loads=data.get('loads', []),
            overload=data.get('overload', 0),
            objective=data.get('objective', 0.0),
            feasible=data.get('feasible', True),
            coverage_valid=data.get('coverage_valid', True),
            conservation_valid=data.get('conservation_valid', True),
            capacity_valid=data.get('capacity_valid', True),
            metrics=data.get('metrics', {})
        )
