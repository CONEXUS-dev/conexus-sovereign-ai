"""
Replay Validator - Verify deterministic replay of recorded runs
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any


class ReplayValidator:
    """
    Validates that replay mode produces identical results to live mode.
    
    This is the core reproducibility guarantee:
    - Live run produces artifacts + hash
    - Replay run with same trace produces identical hash
    """
    
    @staticmethod
    def compute_solution_hash(solution: Dict[str, Any]) -> str:
        """
        Compute deterministic hash of solution.
        
        Hash includes:
        - Assignment vector
        - Routes
        - Distance
        - Loads
        """
        # Extract deterministic fields
        hash_data = {
            'assignment': solution['assignment'],
            'routes': solution['routes'],
            'distance': round(solution['distance'], 6),  # Round to avoid float precision issues
            'loads': solution['loads']
        }
        
        # Convert to canonical JSON
        json_str = json.dumps(hash_data, sort_keys=True)
        
        # Compute SHA256
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    @staticmethod
    def validate_replay(live_dir: str, replay_dir: str) -> tuple[bool, str]:
        """
        Validate that replay matches live run.
        
        Args:
            live_dir: Directory with live run artifacts
            replay_dir: Directory with replay run artifacts
        
        Returns:
            (is_valid, message)
        """
        live_path = Path(live_dir)
        replay_path = Path(replay_dir)
        
        # Load solutions
        try:
            with open(live_path / 'final_solution.json', 'r') as f:
                live_solution = json.load(f)
            
            with open(replay_path / 'final_solution.json', 'r') as f:
                replay_solution = json.load(f)
        except FileNotFoundError as e:
            return False, f"Missing solution file: {e}"
        
        # Compute hashes
        live_hash = ReplayValidator.compute_solution_hash(live_solution)
        replay_hash = ReplayValidator.compute_solution_hash(replay_solution)
        
        # Compare
        if live_hash == replay_hash:
            return True, f"✅ Replay valid: {live_hash[:16]}..."
        else:
            return False, f"❌ Replay mismatch:\n  Live:   {live_hash[:16]}...\n  Replay: {replay_hash[:16]}..."
    
    @staticmethod
    def save_hash(solution_file: str, hash_file: str):
        """Save solution hash to file."""
        with open(solution_file, 'r') as f:
            solution = json.load(f)
        
        solution_hash = ReplayValidator.compute_solution_hash(solution)
        
        with open(hash_file, 'w') as f:
            f.write(solution_hash)
        
        return solution_hash


if __name__ == "__main__":
    # Test hash computation
    test_solution = {
        'id': 'test',
        'assignment': [0, 1, 2, 0, 1],
        'routes': [[0, 3], [1, 4], [2]],
        'distance': 123.456789,
        'loads': [50, 60, 40],
        'objective': 123.456789
    }
    
    hash1 = ReplayValidator.compute_solution_hash(test_solution)
    print(f"Hash 1: {hash1}")
    
    # Same solution should produce same hash
    hash2 = ReplayValidator.compute_solution_hash(test_solution)
    print(f"Hash 2: {hash2}")
    print(f"Match: {hash1 == hash2}")
    
    # Different solution should produce different hash
    test_solution['assignment'][0] = 1
    hash3 = ReplayValidator.compute_solution_hash(test_solution)
    print(f"Hash 3: {hash3}")
    print(f"Different: {hash1 != hash3}")
