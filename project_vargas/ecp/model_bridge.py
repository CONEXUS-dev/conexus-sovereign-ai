# model_bridge.py

import numpy as np
import os
from typing import Tuple, Optional, List
import google.genai as genai
from ecp_substrate import ECPSubstrate
from forgetting_engine import ForgettingEngine


class ModelBridge:
    def __init__(self, substrate: ECPSubstrate, forgetting_engine: ForgettingEngine):
        self.substrate = substrate
        self.engine = forgetting_engine
        self.consensus_threshold = 0.85  # High similarity = consensus = DELETE
        self.distance_threshold = 0.7   # Minimum distance from consensus
        self.alignment_threshold = 0.8  # Minimum alignment with prompt
        # Initialize using SentenceTransformers (working fallback)
        from sentence_transformers import SentenceTransformer
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, text: str) -> np.ndarray:
        """Convert text to normalized embedding vector"""
        try:
            return self.embedding_model.encode(text, normalize_embeddings=True)
        except Exception as e:
            print(f"[BRIDGE] Embedding failed: {e}")
            # Fallback to zero vector
            return np.zeros(384)  # SentenceTransformer dimension

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return float(np.dot(a, b))

    def cosine_distance(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine distance (1 - similarity)"""
        return 1.0 - self.cosine_similarity(a, b)

    def intercept_prompt(self, raw_prompt: str) -> str:
        """Inject active tensions into prompt before model processing"""
        # Get the hardest paradox from substrate if available
        hardest_paradox = self.substrate.pop_hardest_paradox()
        
        if hardest_paradox is None:
            return raw_prompt
        
        # Convert paradox vector back to symbolic context
        # In practice, this would use a decoder or stored text representations
        paradox_context = "[UNRESOLVED TENSION] Active paradox present in substrate"
        
        enhanced_prompt = f"[SYSTEM CONTEXT]\n{paradox_context}\n\n[USER INPUT]\n{raw_prompt}"
        return enhanced_prompt

    def evaluate_response(self, response_text: str, prompt_embedding: np.ndarray) -> Tuple[bool, float, float]:
        """
        Evaluate model response using dual-vector scoring:
        - Distance from consensus (push)
        - Alignment with prompt (tether)
        
        Returns: (passes_filter, distance_score, alignment_score)
        """
        response_embedding = self.embed(response_text)
        
        # Calculate distance from consensus (using substrate state as consensus baseline)
        consensus_distance = self.substrate.compute_tension_gradient(
            response_embedding, 
            self.substrate.state_vector
        )
        
        # Calculate alignment with original prompt
        prompt_alignment = self.cosine_similarity(response_embedding, prompt_embedding)
        
        # Dual-vector test: must have sufficient distance AND alignment
        passes_distance = consensus_distance >= self.distance_threshold
        passes_alignment = prompt_alignment >= self.alignment_threshold
        passes_filter = passes_distance and passes_alignment
        
        return passes_filter, consensus_distance, prompt_alignment

    def process_model_output(self, prompt: str, response: str) -> Tuple[str, bool]:
        """
        Process model output through the interceptor layer.
        If response fails the dual-vector test, signal for regeneration.
        """
        prompt_embedding = self.embed(prompt)
        
        passes_filter, distance_score, alignment_score = self.evaluate_response(response, prompt_embedding)
        
        if passes_filter:
            # Response passes - process through forgetting engine
            response_embedding = self.embed(response)
            self.engine.process_signal(response_embedding)
            return response, True
        else:
            # Response fails - signal for regeneration
            return None, False

    def extract_paradoxes(self, text: str) -> List[str]:
        """
        Extract paradoxical statements from text.
        In practice, this would use more sophisticated NLP.
        For now, returns sentences containing contradiction indicators.
        """
        contradiction_indicators = [
            "but", "however", "yet", "although", "while",
            "paradox", "contradiction", "tension", "conflict"
        ]
        
        sentences = text.split('.')
        paradoxes = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in contradiction_indicators):
                if len(sentence) > 10:  # Filter out short fragments
                    paradoxes.append(sentence)
        
        return paradoxes

    def run_interception_cycle(self, prompt: str, model_generate_fn) -> str:
        """
        Run complete interception cycle until response passes dual-vector test.
        model_generate_fn should be a function that takes a prompt and returns text.
        """
        max_attempts = 5
        attempt = 0
        
        while attempt < max_attempts:
            # Intercept prompt
            enhanced_prompt = self.intercept_prompt(prompt)
            
            # Generate response
            response = model_generate_fn(enhanced_prompt)
            
            # Evaluate response
            processed_response, passes = self.process_model_output(prompt, response)
            
            if passes:
                # Extract any new paradoxes for substrate
                paradoxes = self.extract_paradoxes(processed_response)
                for paradox in paradoxes:
                    paradox_embedding = self.embed(paradox)
                    self.substrate.preserve_paradox(paradox_embedding)
                
                return processed_response
            
            attempt += 1
        
        # If all attempts fail, return the last response with warning
        return f"[FILTER_FAILURE] Could not generate response meeting tension requirements. Last attempt: {response}"
