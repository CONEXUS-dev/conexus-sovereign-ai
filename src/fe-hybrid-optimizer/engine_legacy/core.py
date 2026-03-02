"""
FE Engine Core - Main hybrid control loop
"""

import random
import time
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

from .vrp_instance import VRPInstance
from .candidate import Candidate
from .operators import Operators
from .repair import RepairEngine
from .evaluation import Evaluator
from .paradox import ParadoxBuffer
from pilot.schema import IterationPacket, PilotDecision
from pilot.adapter import PilotAdapter


class FEEngine:
    """
    FE Hybrid Control Engine.
    
    Two-layer architecture:
    - Layer 1 (Engine): Deterministic search substrate
    - Layer 2 (Pilot): AI controller
    
    Supports:
    - Live mode with AI pilot
    - Replay mode with recorded decisions
    - Full logging for reproducibility
    """
    
    def __init__(
        self,
        instance: VRPInstance,
        pilot: PilotAdapter,
        seed: int = 42,
        max_iterations: int = 100,
        population_size: int = 10
    ):
        self.instance = instance
        self.pilot = pilot
        self.seed = seed
        self.max_iterations = max_iterations
        self.population_size = population_size
        
        # Initialize RNG
        self.rng = random.Random(seed)
        
        # Initialize components
        self.operators = Operators(instance, self.rng)
        self.repair = RepairEngine(instance, self.rng)
        self.evaluator = Evaluator(instance)
        self.paradox = ParadoxBuffer(max_size=10)
        
        # State
        self.population: List[Candidate] = []
        self.best_candidate: Optional[Candidate] = None
        self.iteration = 0
        self.stagnation_steps = 0
        self.last_improvement_iteration = 0
        
        # Logging
        self.engine_log: List[Dict[str, Any]] = []
        self.pilot_log: List[Dict[str, Any]] = []
    
    def initialize_population(self) -> None:
        """
        Initialize population with k-means-like clustering.
        """
        self.population = []
        
        for i in range(self.population_size):
            # Create random assignment using spatial clustering
            assignment = self._create_clustered_assignment()
            
            # Repair to ensure feasibility
            assignment, repair_info = self.repair.repair_full(assignment)
            
            # Create candidate
            candidate = Candidate(
                id=f"init_{i}",
                assignment=assignment
            )
            
            # Evaluate
            try:
                self.evaluator.evaluate(candidate)
                self.population.append(candidate)
            except ValueError as e:
                print(f"Warning: Initial candidate {i} invalid: {e}")
                continue
        
        if not self.population:
            raise RuntimeError("Failed to generate any valid initial candidates")
        
        # Set best
        self.best_candidate = min(self.population, key=lambda c: c.objective)
        self.last_improvement_iteration = 0
    
    def _create_clustered_assignment(self) -> List[int]:
        """
        Create assignment using k-means-like spatial clustering.
        """
        n = self.instance.n_customers
        n_vehicles = self.instance.n_vehicles
        
        # Pick random cluster centers
        centers = []
        for _ in range(n_vehicles):
            idx = self.rng.randint(0, n - 1)
            centers.append(self.instance.customer_locations[idx])
        
        # Assign each customer to nearest center
        assignment = []
        for i in range(n):
            loc = self.instance.customer_locations[i]
            distances = [
                ((loc[0] - c[0])**2 + (loc[1] - c[1])**2)**0.5
                for c in centers
            ]
            vehicle = distances.index(min(distances))
            assignment.append(vehicle)
        
        return assignment
    
    def create_iteration_packet(self) -> IterationPacket:
        """
        Create iteration packet for pilot.
        """
        # Calculate load statistics
        loads = self.best_candidate.loads
        loads_sorted = sorted(loads, reverse=True)
        
        # Recent moves (last 5 from log)
        recent_moves = []
        for entry in self.engine_log[-5:]:
            if 'operator' in entry:
                recent_moves.append({
                    'op': entry['operator'],
                    'delta': entry.get('delta', 0),
                    'accepted': entry.get('accepted', False)
                })
        
        # Paradox info
        paradox_best = self.paradox.get_best_alternative()
        
        packet = IterationPacket(
            iteration=self.iteration,
            best_distance=self.best_candidate.distance,
            route_count=len([r for r in self.best_candidate.routes if r]),
            loads_min=min(loads) if loads else 0,
            loads_max=max(loads) if loads else 0,
            loads_mean=sum(loads) / len(loads) if loads else 0,
            loads_top_5=loads_sorted[:5],
            capacity_slack=self.instance.capacity_slack,
            routes_near_capacity=sum(1 for l in loads if l > self.instance.vehicle_capacity * 0.9),
            stagnation_steps=self.stagnation_steps,
            recent_moves=recent_moves,
            paradox_size=self.paradox.size(),
            paradox_best_alt=paradox_best.objective if paradox_best else None,
            feasible=self.best_candidate.feasible,
            overload=self.best_candidate.overload
        )
        
        return packet
    
    def apply_decision(self, decision: PilotDecision) -> None:
        """
        Apply pilot decision to generate new candidates.
        """
        new_candidates = []
        
        if decision.action == 'APPLY_OPERATOR':
            # Generate multiple candidates with specified operator
            for _ in range(5):
                parent = self.rng.choice(self.population)
                new_assignment = self.operators.apply_operator(
                    decision.operator,
                    parent.assignment,
                    parent.routes
                )
                
                # Repair
                new_assignment, repair_info = self.repair.repair_full(new_assignment)
                
                # Create and evaluate
                candidate = Candidate(
                    id=f"iter{self.iteration}_op{decision.operator}",
                    assignment=new_assignment
                )
                
                try:
                    self.evaluator.evaluate(candidate)
                    new_candidates.append(candidate)
                except ValueError as e:
                    print(f"Warning: Candidate invalid after repair: {e}")
                    continue
        
        elif decision.action == 'REPAIR_CAPACITY':
            # Force capacity repair on best candidate
            new_assignment, repair_info = self.repair.repair_capacity(self.best_candidate.assignment)
            
            candidate = Candidate(
                id=f"iter{self.iteration}_repair",
                assignment=new_assignment
            )
            
            try:
                self.evaluator.evaluate(candidate)
                new_candidates.append(candidate)
            except ValueError:
                pass
        
        elif decision.action == 'DIVERSIFY':
            # Pull from paradox buffer or create new random
            if self.paradox.size() > 0:
                paradox_candidate = self.paradox.get_random(self.rng)
                new_candidates.append(paradox_candidate)
            else:
                # Create new random candidate
                assignment = self._create_clustered_assignment()
                assignment, _ = self.repair.repair_full(assignment)
                
                candidate = Candidate(
                    id=f"iter{self.iteration}_diversify",
                    assignment=assignment
                )
                
                try:
                    self.evaluator.evaluate(candidate)
                    new_candidates.append(candidate)
                except ValueError:
                    pass
        
        elif decision.action == 'INTENSIFY':
            # Local search on best candidate
            for _ in range(10):
                new_assignment = self.operators.apply_operator(
                    'swap',
                    self.best_candidate.assignment,
                    self.best_candidate.routes
                )
                
                new_assignment, _ = self.repair.repair_full(new_assignment)
                
                candidate = Candidate(
                    id=f"iter{self.iteration}_intensify",
                    assignment=new_assignment
                )
                
                try:
                    self.evaluator.evaluate(candidate)
                    new_candidates.append(candidate)
                except ValueError:
                    continue
        
        # Add new candidates to population
        self.population.extend(new_candidates)
        
        # Update best
        current_best = min(self.population, key=lambda c: c.objective)
        
        if current_best.objective < self.best_candidate.objective:
            # Improvement found
            delta = self.best_candidate.objective - current_best.objective
            self.best_candidate = current_best
            self.last_improvement_iteration = self.iteration
            self.stagnation_steps = 0
            
            # Log improvement
            self.engine_log.append({
                'iteration': self.iteration,
                'event': 'improvement',
                'new_best': current_best.objective,
                'delta': delta,
                'operator': decision.operator if decision.action == 'APPLY_OPERATOR' else decision.action
            })
        else:
            self.stagnation_steps += 1
        
        # Survival selection: keep best candidates
        self.population.sort(key=lambda c: c.objective)
        self.population = self.population[:self.population_size]
        
        # Add non-best to paradox buffer
        for candidate in self.population[1:]:
            if candidate.objective > self.best_candidate.objective:
                self.paradox.add(candidate)
    
    def run(self, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Run hybrid optimization loop.
        
        Args:
            output_dir: Optional directory to save artifacts
        
        Returns:
            Results dictionary
        """
        start_time = time.time()
        
        # Create output directory
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            pilot_trace_file = str(output_path / 'pilot_trace.jsonl')
        else:
            pilot_trace_file = None
        
        # Initialize
        print("Initializing population...")
        self.initialize_population()
        print(f"Initial best: {self.best_candidate.objective:.2f}")
        
        # Main loop
        for iteration in range(1, self.max_iterations + 1):
            self.iteration = iteration
            
            # Create packet
            packet = self.create_iteration_packet()
            
            # Get pilot decision
            decision = self.pilot.decide(packet, log_file=pilot_trace_file)
            
            # Apply decision
            self.apply_decision(decision)
            
            # Log progress
            if iteration % 10 == 0:
                print(f"Iteration {iteration}/{self.max_iterations}: "
                      f"best={self.best_candidate.objective:.2f}, "
                      f"stagnation={self.stagnation_steps}")
        
        elapsed = time.time() - start_time
        
        # Save artifacts if output_dir specified
        if output_dir:
            self._save_artifacts(output_path, elapsed)
        
        # Return results
        return {
            'best_candidate': self.best_candidate.to_dict(),
            'final_objective': self.best_candidate.objective,
            'final_distance': self.best_candidate.distance,
            'iterations': self.max_iterations,
            'elapsed_seconds': elapsed,
            'feasible': self.best_candidate.feasible
        }
    
    def _save_artifacts(self, output_path: Path, elapsed: float):
        """Save all artifacts for reproducibility."""
        # Instance
        self.instance.save(str(output_path / 'instance.json'))
        
        # Config
        config = {
            'seed': self.seed,
            'max_iterations': self.max_iterations,
            'population_size': self.population_size,
            'pilot_backend': self.pilot.backend_name,
            'elapsed_seconds': elapsed
        }
        with open(output_path / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Final solution
        with open(output_path / 'final_solution.json', 'w') as f:
            json.dump(self.best_candidate.to_dict(), f, indent=2)
        
        # Engine log
        with open(output_path / 'engine_trace.jsonl', 'w') as f:
            for entry in self.engine_log:
                f.write(json.dumps(entry) + '\n')
        
        # Summary
        summary = {
            'distance': self.best_candidate.distance,
            'objective': self.best_candidate.objective,
            'feasible': self.best_candidate.feasible,
            'overload': self.best_candidate.overload,
            'elapsed_seconds': elapsed,
            'iterations': self.max_iterations
        }
        with open(output_path / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nArtifacts saved to: {output_path}")


if __name__ == "__main__":
    # Test engine
    from ..pilot.adapter import PilotAdapter
    
    # Create instance
    instance = VRPInstance.generate_random(
        name="test_25",
        n_customers=25,
        n_vehicles=5,
        vehicle_capacity=100,
        seed=42
    )
    
    # Create pilot
    pilot = PilotAdapter(backend='stub', seed=42)
    pilot.calibrate()
    
    # Create engine
    engine = FEEngine(
        instance=instance,
        pilot=pilot,
        seed=42,
        max_iterations=20,
        population_size=10
    )
    
    # Run
    results = engine.run(output_dir='artifacts/test_run')
    
    print("\nResults:")
    print(f"Distance: {results['final_distance']:.2f}")
    print(f"Objective: {results['final_objective']:.2f}")
    print(f"Feasible: {results['feasible']}")
    print(f"Time: {results['elapsed_seconds']:.2f}s")
