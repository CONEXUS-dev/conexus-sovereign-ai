"""
Paradox Buffer - Memory-only storage for alternative solutions
"""

from typing import List, Optional
from .candidate import Candidate


class ParadoxBuffer:
    """
    Paradox buffer stores alternative solutions that are worse than current best
    but may be useful for diversification.
    
    This is memory-only, not genetic. No crossover or mutation.
    """
    
    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.buffer: List[Candidate] = []
    
    def add(self, candidate: Candidate) -> None:
        """
        Add candidate to buffer.
        Maintains buffer sorted by objective (best first).
        """
        self.buffer.append(candidate)
        self.buffer.sort(key=lambda c: c.objective)
        
        # Keep only max_size best
        if len(self.buffer) > self.max_size:
            self.buffer = self.buffer[:self.max_size]
    
    def get_best_alternative(self) -> Optional[Candidate]:
        """Get best solution from buffer."""
        return self.buffer[0] if self.buffer else None
    
    def get_random(self, rng) -> Optional[Candidate]:
        """Get random solution from buffer."""
        return rng.choice(self.buffer) if self.buffer else None
    
    def size(self) -> int:
        """Current buffer size."""
        return len(self.buffer)
    
    def clear(self) -> None:
        """Clear buffer."""
        self.buffer = []
    
    def to_dict(self) -> dict:
        """Convert to dictionary for logging."""
        return {
            'size': len(self.buffer),
            'best_objective': self.buffer[0].objective if self.buffer else None,
            'solutions': [c.to_dict() for c in self.buffer]
        }
