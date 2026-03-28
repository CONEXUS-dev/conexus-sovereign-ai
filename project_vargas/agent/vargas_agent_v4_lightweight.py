# Vargas Agent V4 - Lightweight Version with ECP Architecture
import sys
import os
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add ECP path
sys.path.append(str(Path(__file__).parent.parent / "ecp"))

# ECP Components
from ecp_substrate import ECPSubstrate
from forgetting_engine import ForgettingEngine

# Constants
ECP_CONTEXT_THRESHOLD = 0.80  # 80% context window tripwire
ECP_MAX_TOKENS = 128000  # Approximate max context for Gemini 1.5 Pro
TOKENS_PER_CHAR = 0.25  # Rough estimate

class LightweightModelBridge:
    """Lightweight version of ModelBridge with hash-based embeddings"""
    
    def __init__(self, substrate, engine):
        self.substrate = substrate
        self.engine = engine
        self.consensus_threshold = 0.85
        self.distance_threshold = 0.7
        self.alignment_threshold = 0.8
    
    def embed(self, text: str) -> np.ndarray:
        """Create lightweight hash-based embeddings"""
        text_hash = hash(text)
        np.random.seed(text_hash % (2**32))
        return np.random.rand(384)
    
    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return float(np.dot(a, b))
    
    def cosine_distance(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine distance (1 - similarity)"""
        return 1.0 - self.cosine_similarity(a, b)
    
    def intercept_prompt(self, raw_prompt: str) -> str:
        """Intercept and process prompt through ECP"""
        # Convert prompt to embedding
        prompt_embedding = self.embed(raw_prompt)
        
        # Process through substrate
        state, tension = self.substrate.process_stage(prompt_embedding)
        
        # Check if tension exceeds threshold
        if tension > self.substrate.threshold:
            # High tension: preserve paradox, modify prompt
            paradox_note = "\n[PARADOX DETECTED: Preserving tension]"
            return raw_prompt + paradox_note
        else:
            # Low tension: consensus, return as-is
            return raw_prompt

class LightweightMemoryCompressor:
    """Lightweight version of TensionCompressor"""
    
    def __init__(self, substrate, retention_threshold: float = 0.75):
        self.substrate = substrate
        self.retention_threshold = retention_threshold
        self.compression_directive = """
        You are compressing conversation history for archival. CRITICAL CONSTRAINT: 
        Do NOT harmonize or resolve contradictions. Do NOT smooth tensions. 
        Your task is to identify and preserve the exact points of friction, 
        the competing vectors, and the suspended paradoxes. 
        Compress the density without eliminating the tension. 
        Map the structural load, not the narrative resolution.
        """
    
    def embed(self, text: str) -> np.ndarray:
        """Create lightweight embeddings"""
        text_hash = hash(text)
        np.random.seed(text_hash % (2**32))
        return np.random.rand(384)
    
    def calculate_tension_score(self, text: str) -> float:
        """Calculate tension score for text"""
        embedding = self.embed(text)
        return self.substrate.compute_tension_gradient(embedding, self.substrate.state_vector)
    
    def compress_conversation(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Compress conversation while preserving tension"""
        if not conversation_history:
            return ""
        
        # Calculate tension for each message
        tension_scores = []
        for msg in conversation_history:
            text = msg.get("content", "")
            score = self.calculate_tension_score(text)
            tension_scores.append(score)
        
        # Sort by tension (highest first)
        sorted_msgs = sorted(zip(conversation_history, tension_scores), key=lambda x: x[1], reverse=True)
        
        # Compress high-tension messages
        compressed = []
        for msg, score in sorted_msgs:
            if score >= self.retention_threshold:
                content = msg.get("content", "")[:200]  # Truncate
                compressed.append(f"[Tension: {score:.3f}] {content}")
        
        return "\n".join(compressed)

class LightweightRecursiveReinjection:
    """Lightweight version of RecursiveReinjection"""
    
    def __init__(self, substrate, engine, bridge):
        self.substrate = substrate
        self.engine = engine
        self.bridge = bridge
        self.survival_threshold = 3
        self.artifacts = []
    
    def embed(self, text: str) -> np.ndarray:
        """Create lightweight embeddings"""
        text_hash = hash(text)
        np.random.seed(text_hash % (2**32))
        return np.random.rand(384)
    
    def query_most_recent_paradox(self) -> Optional[str]:
        """Query for most recent paradox"""
        hardest_paradox = self.substrate.pop_hardest_paradox()
        
        if hardest_paradox is None:
            return None
        
        # Convert vector back to text placeholder
        return "[PARADOX: High-tension vector preserved]"
    
    def run_recursive_cycle(self, seed_text: str, num_cycles: int = 3, model_generate_fn=None) -> Dict[str, Any]:
        """Run recursive reinjection cycle"""
        cycles_completed = 0
        artifacts_created = []
        
        for cycle in range(num_cycles):
            # Get current paradox
            paradox = self.query_most_recent_paradox()
            
            if paradox is None:
                # Create initial paradox from seed
                seed_embedding = self.embed(seed_text)
                self.substrate.preserve_paradox(seed_embedding)
                artifacts_created.append(f"Cycle {cycle}: Created initial paradox")
            else:
                # Reinject paradox
                if model_generate_fn:
                    response = model_generate_fn(f"Process this paradox: {paradox}")
                    response_embedding = self.embed(response)
                    self.substrate.preserve_paradox(response_embedding)
                    artifacts_created.append(f"Cycle {cycle}: Reinjected paradox")
                else:
                    artifacts_created.append(f"Cycle {cycle}: Paradox available but no model")
            
            cycles_completed += 1
        
        return {
            "cycles_completed": cycles_completed,
            "artifacts_created": artifacts_created,
            "final_paradox_count": len(self.substrate.paradox_archive)
        }

class VargasAgentV4Lightweight:
    """Vargas Agent V4 - Lightweight Version with ECP Architecture"""
    
    def __init__(self):
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # ECP Components
        self.substrate = ECPSubstrate(dimensions=384, base_threshold=0.618)
        self.forgetting_engine = ForgettingEngine(self.substrate, retention_threshold=0.3)
        self.model_bridge = LightweightModelBridge(self.substrate, self.forgetting_engine)
        self.memory_compressor = LightweightMemoryCompressor(self.substrate, retention_threshold=0.75)
        self.reinjector = LightweightRecursiveReinjection(self.substrate, self.forgetting_engine, self.model_bridge)
        
        # ECP State tracking
        self.context_tokens_used = 0
        self.compression_triggered = False
        
        # Conversation history
        self.conversation_history = []
        
        self.logger.info("🚀 Vargas V4 Lightweight Agent Initialized")
        self.logger.info("✅ ECP Architecture: Active")
        self.logger.info("✅ Embeddings: Lightweight (hash-based)")
        self.logger.info("✅ Paradox Processing: Enabled")
        self.logger.info("✅ 80% Context Tripwire: Armed")
    
    def check_context_tripwire(self, prompt: str) -> bool:
        """Check if context exceeds 80% threshold"""
        estimated_tokens = len(prompt) * TOKENS_PER_CHAR
        self.context_tokens_used += estimated_tokens
        
        if self.context_tokens_used > (ECP_MAX_TOKENS * ECP_CONTEXT_THRESHOLD):
            if not self.compression_triggered:
                self.logger.warning(f"🚨 80% Context Tripwire Activated! Used: {self.context_tokens_used:.0f}")
                self.compression_triggered = True
                return True
        
        return False
    
    def trigger_memory_compression(self) -> str:
        """Trigger autonomous memory compression"""
        self.logger.info("🔄 Triggering Memory Compression...")
        
        # Compress conversation history
        compressed = self.memory_compressor.compress_conversation(self.conversation_history)
        
        # Reset context tracking
        self.context_tokens_used = 0
        self.compression_triggered = False
        
        # Clear old history
        self.conversation_history = []
        
        self.logger.info(f"✅ Compression complete. Preserved {len(compressed)} characters")
        return compressed
    
    def process_message(self, user_input: str) -> Dict[str, Any]:
        """Process user message through V4 ECP architecture"""
        self.logger.info(f"📥 Processing: {user_input[:50]}...")
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": np.datetime64('now').astype(str)
        })
        
        # Check context tripwire
        if self.check_context_tripwire(user_input):
            compressed = self.trigger_memory_compression()
            self.logger.info("📦 Memory compression completed")
        
        # Process through model bridge
        processed_prompt = self.model_bridge.intercept_prompt(user_input)
        
        # Process through forgetting engine
        input_embedding = self.model_bridge.embed(user_input)
        self.forgetting_engine.process_signal(input_embedding)
        
        # Generate response (mock for now)
        response = f"V4 Response to: {user_input[:30]}..."
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant", 
            "content": response,
            "timestamp": np.datetime64('now').astype(str)
        })
        
        # Get ECP status
        ecp_status = self.get_ecp_status()
        
        return {
            "response": response,
            "ecp_status": ecp_status,
            "context_used": self.context_tokens_used,
            "compression_active": self.compression_triggered
        }
    
    def get_ecp_status(self) -> Dict[str, Any]:
        """Get current ECP status"""
        substrate_metrics = self.substrate.get_metrics()
        engine_summary = self.forgetting_engine.summary()
        
        return {
            "substrate": {
                "stage": substrate_metrics.stage_index,
                "threshold": substrate_metrics.active_threshold,
                "paradox_count": substrate_metrics.paradox_count,
                "vector_magnitude": substrate_metrics.vector_magnitude
            },
            "forgetting_engine": {
                "active_traces": engine_summary["active_traces"],
                "current_cycle": engine_summary["current_cycle"],
                "total_deleted": engine_summary["total_deleted"],
                "total_promoted": engine_summary["total_promoted"]
            },
            "memory_state": {
                "context_tokens": self.context_tokens_used,
                "compression_triggered": self.compression_triggered,
                "conversation_length": len(self.conversation_history)
            }
        }
    
    def run_recursive_cycle(self, seed_text: str, num_cycles: int = 3) -> Dict[str, Any]:
        """Run recursive reinjection cycle"""
        def mock_model_generate(prompt: str) -> str:
            return f"Mock response to: {prompt[:50]}..."
        
        return self.reinjector.run_recursive_cycle(seed_text, num_cycles, mock_model_generate)

def create_vargas_agent_v4_lightweight():
    """Create Vargas V4 Lightweight agent"""
    return VargasAgentV4Lightweight()

def main():
    """Run V4 Lightweight agent demo"""
    print("🚀 Vargas V4 Lightweight Agent Demo")
    print("=" * 50)
    
    # Create agent
    agent = create_vargas_agent_v4_lightweight()
    
    # Test messages
    test_messages = [
        "Hello Vargas, how does the ECP architecture work?",
        "Can you explain paradox preservation?",
        "What happens when tension exceeds the threshold?",
        "How does the forgetting engine decide what to delete?",
        "Show me the 80% context tripwire in action",
        "This is a long message that should trigger the context tripwire eventually because we need to test the autonomous memory compression feature that activates when the context window reaches 80% of the maximum token limit which is set to 128000 tokens for Gemini 1.5 Pro"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📨 Message {i}: {message[:50]}...")
        
        result = agent.process_message(message)
        
        print(f"📤 Response: {result['response']}")
        print(f"📊 Context Used: {result['context_used']:.0f} tokens")
        print(f"🚨 Compression: {'Active' if result['compression_active'] else 'Inactive'}")
        print(f"🧠 Paradox Count: {result['ecp_status']['substrate']['paradox_count']}")
        print(f"🔄 Active Traces: {result['ecp_status']['forgetting_engine']['active_traces']}")
    
    # Test recursive cycle
    print(f"\n🔄 Testing Recursive Reinjection...")
    cycle_result = agent.run_recursive_cycle("Test paradox seed", num_cycles=3)
    print(f"✅ Cycles Completed: {cycle_result['cycles_completed']}")
    print(f"✅ Artifacts Created: {len(cycle_result['artifacts_created'])}")
    
    # Final status
    final_status = agent.get_ecp_status()
    print(f"\n📊 Final ECP Status:")
    print(f"  Stage: {final_status['substrate']['stage']}")
    print(f"  Threshold: {final_status['substrate']['threshold']:.3f}")
    print(f"  Paradoxes: {final_status['substrate']['paradox_count']}")
    print(f"  Deleted: {final_status['forgetting_engine']['total_deleted']}")
    print(f"  Promoted: {final_status['forgetting_engine']['total_promoted']}")
    
    print("\n🎉 Vargas V4 Lightweight Demo Complete!")

if __name__ == "__main__":
    main()
