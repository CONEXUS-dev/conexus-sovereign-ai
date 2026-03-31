# paradox_engine.py
"""
Formal Paradox Engine for V4 Architecture
Implements contradiction detection with cosine similarity thresholds per blueprint specification.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import logging

from .ecp_substrate import ECPSubstrate
from .forgetting_engine import ForgettingEngine

logger = logging.getLogger(__name__)

@dataclass
class ParadoxObject:
    """Represents a detected contradiction with E-Vector delta."""
    topic_vector: np.ndarray
    implication_vector_a: np.ndarray
    implication_vector_b: np.ndarray
    topic_similarity: float
    implication_similarity: float
    semantic_distance: float
    confidence: float
    detected_at: str
    e_vector_delta: Dict[str, float]
    source_text: str

class ParadoxEngine:
    """
    Formal Paradox Engine for V4 Architecture
    
    Detects contradictions using cosine similarity thresholds:
    - Topic similarity > 0.8 (proximate in topic)
    - Implication similarity < 0.2 (distant in implication)
    
    Outputs E-Vector delta rather than logical resolution.
    """
    
    def __init__(self, substrate: ECPSubstrate, forgetting_engine: ForgettingEngine):
        self.substrate = substrate
        self.engine = forgetting_engine
        
        # Blueprint thresholds
        self.topic_similarity_min = 0.8
        self.implication_similarity_max = 0.2
        
        # Paradox archive for tracking
        self.paradox_archive: List[ParadoxObject] = []
        self.detection_count = 0
        self.last_detection_time = None
        
    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def detect_contradiction(
        self,
        topic_vector_a: np.ndarray,
        topic_vector_b: np.ndarray,
        implication_vector_a: np.ndarray,
        implication_vector_b: np.ndarray,
        source_text: str = ""
    ) -> Optional[ParadoxObject]:
        """
        Detect contradiction between two data points using blueprint thresholds.
        
        Args:
            topic_vector_a: First topic embedding
            topic_vector_b: Second topic embedding  
            implication_vector_a: First implication embedding
            implication_vector_b: Second implication embedding
            source_text: Original text that generated this detection
            metadata: Additional context information
            
        Returns:
            ParadoxObject if contradiction detected, None otherwise
        """
        # Calculate similarities
        topic_sim = self.cosine_similarity(topic_vector_a, topic_vector_b)
        impl_sim = self.cosine_similarity(implication_vector_a, implication_vector_b)
        
        # Apply blueprint thresholds
        if topic_sim > self.topic_similarity_min and impl_sim < self.implication_similarity_max:
            # Contradiction detected: topic-proximate but implication-divergent
            semantic_distance = 1.0 - impl_sim  # Distance from consensus
            confidence = min(topic_sim, 1.0 - impl_sim)  # Confidence based on divergence
            
            # Calculate E-Vector delta
            combined_vector = (topic_vector_a + topic_vector_b + implication_vector_a + implication_vector_b) / 4.0
            e_vector_delta = self._compute_e_vector_delta(
                combined_vector, combined_vector,
                combined_vector, combined_vector,
                semantic_distance
            )
            
            paradox = ParadoxObject(
                topic_vector=topic_vector_a.copy(),
                implication_vector_a=implication_vector_a.copy(),
                implication_vector_b=implication_vector_b.copy(),
                topic_similarity=topic_sim,
                implication_similarity=impl_sim,
                semantic_distance=semantic_distance,
                confidence=confidence,
                detected_at=datetime.now(timezone.utc).isoformat(),
                e_vector_delta=e_vector_delta,
                source_text=source_text
            )
            
            self.paradox_archive.append(paradox)
            self.detection_count += 1
            self.last_detection_time = paradox.detected_at
            
            logger.info(
                "[PARADOX] Contradiction detected: topic_sim=%.3f, impl_sim=%.3f, confidence=%.3f",
                topic_sim, impl_sim, confidence
            )
            
            return paradox
        
        return None
    
    def _compute_e_vector_delta(
        self,
        _topic_a: np.ndarray,
        _topic_b: np.ndarray,
        _impl_a: np.ndarray,
        _impl_b: np.ndarray,
        semantic_distance: float
    ) -> Dict[str, float]:
        """
        Compute E-Vector delta based on detected contradiction.
        
        E-Vector dimensions from blueprint:
        - entropy_level: System complexity tolerance
        - chaos_threshold: Contradiction tolerance  
        - challenge_threshold: Intervention readiness
        - initiative_timer: Action timing
        """
        # Base delta from semantic distance (higher distance = higher entropy)
        entropy_boost = min(semantic_distance * 0.5, 0.8)  # Cap at 0.8
        
        # Chaos threshold increases with contradiction strength
        chaos_boost = semantic_distance * 0.6
        
        # Challenge threshold increases with confidence
        challenge_boost = min(semantic_distance * 0.4, 0.6)
        
        # Initiative timer decreases with higher tension (faster response)
        initiative_adjustment = -semantic_distance * 10  # Scale to seconds
        
        return {
            "entropy_level": min(0.5 + entropy_boost, 1.0),
            "chaos_threshold": min(0.5 + chaos_boost, 1.0),
            "challenge_threshold": min(0.7 + challenge_boost, 1.0),
            "initiative_timer": max(30 + initiative_adjustment, 5)  # Min 5 seconds
        }
    
    def process_paradox(self, paradox: ParadoxObject) -> Dict[str, Any]:
        """
        Process a detected paradox through the ECP system.
        
        Args:
            paradox: The detected paradox object
            
        Returns:
            Processing result with ECP system response
        """
        # Calculate tension gradient for the paradox
        combined_vector = (paradox.topic_vector + paradox.implication_vector_a + paradox.implication_vector_b) / 3.0
        tension = self.substrate.compute_tension_gradient(combined_vector, self.substrate.state_vector)
        
        # Process through forgetting engine
        self.engine.process_signal(combined_vector)
        
        # Apply E-Vector delta to substrate state
        for dim, delta in paradox.e_vector_delta.items():
            if dim in self.substrate.state_vector:
                # Apply delta with bounds checking
                current_value = self.substrate.state_vector[dim]
                new_value = np.clip(current_value + delta, 0.0, 1.0)
                self.substrate.state_vector[dim] = new_value
        
        # Store paradox in substrate archive
        self.substrate.preserve_paradox(combined_vector)
        
        return {
            "paradox_id": len(self.paradox_archive),
            "tension": tension,
            "e_vector_state": self.substrate.state_vector.copy() if hasattr(self.substrate.state_vector, 'copy') else self.substrate.state_vector,
            "engine_status": self.engine.summary(),
            "processing_time": datetime.now(timezone.utc).isoformat()
        }
    
    def get_recent_paradoxes(self, limit: int = 10) -> List[ParadoxObject]:
        """Get the most recently detected paradoxes."""
        return self.paradox_archive[-limit:] if self.paradox_archive else []
    
    def get_paradox_statistics(self) -> Dict[str, Any]:
        """Get statistics about paradox detection."""
        if not self.paradox_archive:
            return {
                "total_detections": 0,
                "avg_confidence": 0.0,
                "avg_topic_similarity": 0.0,
                "avg_implication_similarity": 0.0,
                "avg_semantic_distance": 0.0
            }
        
        confidences = [p.confidence for p in self.paradox_archive]
        topic_sims = [p.topic_similarity for p in self.paradox_archive]
        impl_sims = [p.implication_similarity for p in self.paradox_archive]
        distances = [p.semantic_distance for p in self.paradox_archive]
        
        return {
            "total_detections": self.detection_count,
            "avg_confidence": np.mean(confidences),
            "avg_topic_similarity": np.mean(topic_sims),
            "avg_implication_similarity": np.mean(impl_sims),
            "avg_semantic_distance": np.mean(distances),
            "last_detection": self.last_detection_time,
            "archive_size": len(self.paradox_archive),
            "substrate_state": self.substrate.summary(),
            "engine_state": self.engine.summary()
        }
    
    def validate_thresholds(self) -> bool:
        """Validate that thresholds match blueprint specifications."""
        epsilon = 1e-9  # Small epsilon for float comparison
        return (
            abs(self.topic_similarity_min - 0.8) < epsilon and
            abs(self.implication_similarity_max - 0.2) < epsilon
        )
    
    def update_thresholds(self, topic_min: Optional[float] = None, impl_max: Optional[float] = None):
        """
        Update detection thresholds (for calibration).
        
        Args:
            topic_min: New topic similarity minimum threshold
            impl_max: New implication similarity maximum threshold
        """
        if topic_min is not None:
            self.topic_similarity_min = topic_min
            logger.info(f"[PARADOX] Updated topic similarity threshold to {topic_min}")
        
        if impl_max is not None:
            self.implication_similarity_max = impl_max
            logger.info(f"[PARADOX] Updated implication similarity threshold to {impl_max}")
    
    def clear_archive(self):
        """Clear the paradox archive (for testing or reset)."""
        self.paradox_archive.clear()
        self.detection_count = 0
        self.last_detection_time = None
        logger.info("[PARADOX] Archive cleared")
