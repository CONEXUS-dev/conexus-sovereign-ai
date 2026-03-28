# memory_compression.py

import numpy as np
import os
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from ecp_substrate import ECPSubstrate
import google.genai as genai


class TensionCompressor:
    def __init__(self, substrate: ECPSubstrate, retention_threshold: float = 0.75):
        self.substrate = substrate
        self.retention_threshold = retention_threshold
        # Initialize using SentenceTransformers (working fallback)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.compression_directive = """
        You are compressing conversation history for archival. CRITICAL CONSTRAINT: 
        Do NOT harmonize or resolve contradictions. Do NOT smooth tensions. 
        Your task is to identify and preserve the exact points of friction, 
        the competing vectors, and the suspended paradoxes. 
        Compress the density without eliminating the tension. 
        Map the structural load, not the narrative resolution.
        """

    def embed(self, text: str) -> np.ndarray:
        """Convert text to normalized embedding vector"""
        try:
            return self.embedding_model.encode(text, normalize_embeddings=True)
        except Exception as e:
            print(f"[COMPRESSOR] Embedding failed: {e}")
            # Fallback to zero vector
            return np.zeros(384)  # SentenceTransformer dimension

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return float(np.dot(a, b))

    def calculate_tension_score(self, text: str) -> float:
        """
        Calculate tension score for a text block based on its distance from 
        the substrate's current state and internal contradictions.
        """
        text_embedding = self.embed(text)
        
        # Distance from substrate state (proxy for novelty/tension)
        tension_from_substrate = self.substrate.compute_tension_gradient(
            text_embedding, 
            self.substrate.state_vector
        )
        
        # Internal contradiction detection (simple heuristic)
        contradiction_indicators = [
            "but", "however", "yet", "although", "while", "whereas",
            "paradox", "contradiction", "tension", "conflict", "versus"
        ]
        
        internal_contradiction_score = 0.0
        sentences = text.split('.')
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in contradiction_indicators):
                internal_contradiction_score += 0.1
        
        # Combine scores
        total_tension = tension_from_substrate + min(internal_contradiction_score, 0.5)
        return float(total_tension)

    def extract_competing_vectors(self, text: str) -> List[Dict[str, str]]:
        """
        Extract competing thesis/antithesis pairs from text.
        This is a simplified implementation - in practice would use more sophisticated NLP.
        """
        vectors = []
        
        # Look for contrastive constructions
        contrastive_patterns = [
            ("on one hand", "on the other hand"),
            ("while", "whereas"),
            ("although", "nevertheless"),
            ("some argue", "others claim"),
            ("the advantage", "the disadvantage")
        ]
        
        for pattern in contrastive_patterns:
            if pattern[0] in text.lower() and pattern[1] in text.lower():
                # Extract surrounding context (simplified)
                vectors.append({
                    "type": "contrastive_pair",
                    "pattern": pattern,
                    "context": text[text.lower().find(pattern[0]):text.lower().find(pattern[1]) + 50]
                })
        
        return vectors

    def compress_with_llm(self, memory_blocks: List[str]) -> str:
        """
        Use LLM to compress memory blocks while preserving tension.
        This would connect to the actual LLM client in production.
        """
        # Simplified implementation - in practice would call Gemini/GPT
        combined_text = "\n\n".join(memory_blocks)
        
        # For now, return a truncated version with tension markers
        compressed_blocks = []
        for block in memory_blocks:
            tension_score = self.calculate_tension_score(block)
            if tension_score >= self.retention_threshold:
                # High tension - preserve with marker
                compressed_blocks.append(f"[HIGH_TENSION:{tension_score:.2f}] {block[:500]}...")
            else:
                # Low tension - compress more aggressively
                compressed_blocks.append(f"[LOW_TENSION:{tension_score:.2f}] {block[:200]}...")
        
        return "\n\n".join(compressed_blocks)

    def compress_memory_blocks(self, memory_blocks: List[str], tension_scores: List[float]) -> Dict[str, Any]:
        """
        Compress memory blocks based on tension scores while preserving paradoxes.
        """
        if len(memory_blocks) != len(tension_scores):
            raise ValueError("memory_blocks and tension_scores must have same length")
        
        compression_result = {
            "preserved_blocks": [],
            "compressed_blocks": [],
            "competing_vectors": [],
            "suspended_paradoxes": [],
            "compression_ratio": 0.0,
            "tension_preservation": 0.0
        }
        
        original_chars = sum(len(block) for block in memory_blocks)
        
        for block, score in zip(memory_blocks, tension_scores):
            if score >= self.retention_threshold:
                # High tension - preserve losslessly with metadata
                vectors = self.extract_competing_vectors(block)
                compression_result["preserved_blocks"].append({
                    "content": block,
                    "tension_score": score,
                    "vectors": vectors
                })
                compression_result["competing_vectors"].extend(vectors)
            else:
                # Low tension - compress
                compressed = f"[COMPRESSED] {block[:100]}..." if len(block) > 100 else block
                compression_result["compressed_blocks"].append({
                    "content": compressed,
                    "original_tension": score
                })
        
        # Create suspended paradox summary
        if compression_result["competing_vectors"]:
            paradox_summary = "SUSPENDED PARADOXES:\n"
            for i, vector in enumerate(compression_result["competing_vectors"][:5]):  # Top 5
                paradox_summary += f"{i+1}. {vector.get('context', 'Unknown tension')}\n"
            compression_result["suspended_paradoxes"] = paradox_summary
        
        # Calculate metrics
        compressed_chars = sum(
            len(item["content"]) for item in compression_result["preserved_blocks"] + compression_result["compressed_blocks"]
        )
        compression_result["compression_ratio"] = compressed_chars / original_chars if original_chars > 0 else 0
        
        preserved_tension = sum(score for score in tension_scores if score >= self.retention_threshold)
        total_tension = sum(tension_scores)
        compression_result["tension_preservation"] = preserved_tension / total_tension if total_tension > 0 else 0
        
        return compression_result

    def create_compression_payload(self, compression_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create payload for writing to Qdrant with tension preservation metadata.
        """
        payload = {
            "type": "memory_compression",
            "timestamp": np.datetime64('now').astype('int64'),
            "compression_ratio": compression_result["compression_ratio"],
            "tension_preservation": compression_result["tension_preservation"],
            "preserved_count": len(compression_result["preserved_blocks"]),
            "compressed_count": len(compression_result["compressed_blocks"]),
            "suspended_paradoxes": compression_result["suspended_paradoxes"],
            "content": {
                "preserved": compression_result["preserved_blocks"],
                "compressed": compression_result["compressed_blocks"],
                "vectors": compression_result["competing_vectors"]
            },
            "substrate_state": self.substrate.summary()
        }
        
        return payload

    def autonomous_compression_cycle(self, memory_blocks: List[str]) -> Dict[str, Any]:
        """
        Run the full autonomous compression cycle as described in the transcript.
        """
        # Calculate tension scores for all blocks
        tension_scores = [self.calculate_tension_score(block) for block in memory_blocks]
        
        # Compress based on tension
        compression_result = self.compress_memory_blocks(memory_blocks, tension_scores)
        
        # Create payload for storage
        payload = self.create_compression_payload(compression_result)
        
        return payload
