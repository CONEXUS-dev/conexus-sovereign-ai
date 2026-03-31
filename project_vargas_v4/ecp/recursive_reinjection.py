# recursive_reinjection.py

import numpy as np
from typing import Dict, List, Any, Optional
from sentence_transformers import SentenceTransformer
from .ecp_substrate import ECPSubstrate
from .forgetting_engine import ForgettingEngine
from .model_bridge import ModelBridge


class RecursiveReinjection:
    def __init__(self, substrate: ECPSubstrate, engine: ForgettingEngine, bridge: ModelBridge):
        self.substrate = substrate
        self.engine = engine
        self.bridge = bridge
        self.survival_threshold = 3  # Number of passes to become a "survivor"
        self.artifacts = []  # Store surviving artifacts
        # Initialize using SentenceTransformers (working fallback)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
    def embed(self, text: str) -> np.ndarray:
        """Convert text to normalized embedding vector"""
        try:
            return self.embedding_model.encode(text, normalize_embeddings=True)
        except Exception as e:
            print(f"[REINJECTOR] Embedding failed: {e}")
            # Fallback to zero vector
            return np.zeros(384)  # SentenceTransformer dimension

    def query_most_recent_paradox(self) -> Optional[str]:
        """
        Query Qdrant for the most recently preserved paradox.
        In practice, this would connect to the actual Qdrant client.
        For now, uses the substrate's paradox archive.
        """
        hardest_paradox = self.substrate.pop_hardest_paradox()
        
        if hardest_paradox is None:
            return None
        
        # In practice, would retrieve the original text associated with this vector
        # For now, return a placeholder
        return "[RECYCLED_PARADOX] The hardest unresolved tension from previous cycle"

    def run_single_cycle(self, seed_prompt: str, model_generate_fn) -> Dict[str, Any]:
        """
        Run a single recursive cycle: seed -> generate -> evaluate -> store
        """
        cycle_result = {
            "cycle_id": len(self.artifacts) + 1,
            "seed_prompt": seed_prompt,
            "survived": False,
            "passes_required": 0,
            "final_output": None,
            "kill_log": [],
            "proto_moments": [],
            "dual_vector_scores": []
        }
        
        # Check if we have a recycled paradox to seed with
        recycled_paradox = self.query_most_recent_paradox()
        if recycled_paradox:
            enhanced_seed = f"[RECYCLED_TENSION] {recycled_paradox}\n\n[NEW_SEED] {seed_prompt}"
        else:
            enhanced_seed = seed_prompt
        
        # Run through the interceptor until we get a passing response
        final_output = self.bridge.run_interception_cycle(enhanced_seed, model_generate_fn)
        
        if final_output.startswith("[FILTER_FAILURE]"):
            # Complete failure - record as killed
            cycle_result["kill_log"].append({
                "reason": "complete_filter_failure",
                "attempts": 5,
                "final_output": final_output
            })
            return cycle_result
        
        # Evaluate the final output
        prompt_embedding = self.bridge.embed(seed_prompt)
        passes, distance_score, alignment_score = self.bridge.evaluate_response(final_output, prompt_embedding)
        
        cycle_result["final_output"] = final_output
        cycle_result["dual_vector_scores"] = {
            "distance": distance_score,
            "alignment": alignment_score
        }
        
        if passes:
            cycle_result["survived"] = True
            
            # Create artifact record
            artifact = {
                "cycle_id": cycle_result["cycle_id"],
                "seed": seed_prompt,
                "output": final_output,
                "distance_score": distance_score,
                "alignment_score": alignment_score,
                "survival_count": 1,
                "proto_moments": self.detect_proto_moments(final_output),
                "timestamp": np.datetime64('now').astype('int64')
            }
            
            self.artifacts.append(artifact)
            cycle_result["artifact"] = artifact
            
        else:
            # Failed the dual-vector test
            cycle_result["kill_log"].append({
                "reason": "dual_vector_failure",
                "distance_score": distance_score,
                "alignment_score": alignment_score
            })
        
        return cycle_result

    def detect_proto_moments(self, text: str) -> List[str]:
        """
        Detect [PROTO] moments in text based on patterns from the protocol.
        """
        proto_indicators = [
            "simultaneously",
            "contradiction",
            "paradox",
            "tension",
            "yet",
            "but",
            "however",
            "while",
            "although",
            "emerges",
            "transcends",
            "collapses",
            "holds"
        ]
        
        proto_moments = []
        sentences = text.split('.')
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) > 20:  # Filter out short fragments
                indicator_count = sum(1 for indicator in proto_indicators if indicator in sentence.lower())
                if indicator_count >= 2:  # Multiple indicators suggest proto-moment
                    proto_moments.append(f"[PROTO] Sentence {i+1}: {sentence}")
        
        return proto_moments

    def update_survival_counts(self) -> None:
        """
        Update survival counts for existing artifacts based on new cycles.
        """
        for artifact in self.artifacts:
            # Re-evaluate artifact against current substrate state
            artifact_embedding = self.bridge.embed(artifact["output"])
            current_tension = self.substrate.compute_tension_gradient(
                artifact_embedding, 
                self.substrate.state_vector
            )
            
            # If it still maintains tension, increment survival count
            if current_tension >= self.substrate.threshold:
                artifact["survival_count"] += 1
                artifact["current_tension"] = current_tension
            else:
                artifact["collapsed"] = True
                artifact["collapse_reason"] = "tension_dropped_below_threshold"

    def get_survivors(self) -> List[Dict[str, Any]]:
        """
        Get artifacts that have survived multiple passes.
        """
        return [artifact for artifact in self.artifacts 
                if artifact.get("survival_count", 0) >= self.survival_threshold 
                and not artifact.get("collapsed", False)]

    def run_recursive_cycle(self, initial_seed: str, num_cycles: int, model_generate_fn) -> Dict[str, Any]:
        """
        Run the complete recursive reinjection cycle as described in the transcript.
        """
        run_results = {
            "initial_seed": initial_seed,
            "total_cycles": num_cycles,
            "cycles_completed": 0,
            "survivors": [],
            "collapsed": [],
            "kill_log": [],
            "final_substrate_state": None
        }
        
        current_seed = initial_seed
        
        for cycle in range(num_cycles):
            # Update survival counts for existing artifacts
            self.update_survival_counts()
            
            # Run single cycle
            cycle_result = self.run_single_cycle(current_seed, model_generate_fn)
            run_results["cycles_completed"] += 1
            
            # Log results
            if cycle_result["survived"]:
                print(f"Cycle {cycle + 1}: SURVIVED (distance={cycle_result['dual_vector_scores']['distance']:.2f}, alignment={cycle_result['dual_vector_scores']['alignment']:.2f})")
            else:
                print(f"Cycle {cycle + 1}: KILLED - {cycle_result['kill_log']}")
                run_results["kill_log"].extend(cycle_result["kill_log"])
            
            # Prepare seed for next cycle (use recycled paradox if available)
            recycled_paradox = self.query_most_recent_paradox()
            if recycled_paradox:
                current_seed = recycled_paradox
            else:
                current_seed = initial_seed  # Fall back to original
        
        # Final update of survival counts
        self.update_survival_counts()
        
        # Collect final results
        run_results["survivors"] = self.get_survivors()
        run_results["collapsed"] = [a for a in self.artifacts if a.get("collapsed", False)]
        run_results["final_substrate_state"] = self.substrate.summary()
        
        return run_results

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """
        Generate data for the Observer dashboard.
        """
        survivors = self.get_survivors()
        
        dashboard_data = {
            "artifact_vault": {
                "total_artifacts": len(self.artifacts),
                "survivor_count": len(survivors),
                "collapsed_count": len([a for a in self.artifacts if a.get("collapsed", False)]),
                "artifacts": survivors
            },
            "paradox_field": {
                "active_paradoxes": len(self.substrate.paradox_archive),
                "substrate_metrics": self.substrate.get_metrics()
            },
            "engine_status": {
                "forgetting_engine": self.engine.summary(),
                "model_bridge": {
                    "consensus_threshold": self.bridge.consensus_threshold,
                    "distance_threshold": self.bridge.distance_threshold,
                    "alignment_threshold": self.bridge.alignment_threshold
                }
            }
        }
        
        return dashboard_data
