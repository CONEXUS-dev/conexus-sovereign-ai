# vargas_agent_v4.py
"""
Vargas V4 Unified Agent with ECP Integration
Implements sovereign architecture with paradox detection and bounded tool execution.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from agent.sovereign_state import initialize_sovereign_state
from adapters.cloud_llm.gemini_client import GeminiLLMClient
from memory.memory_client import VargasMemoryClient
from memory.e_vector import EVectorSystem
from ecp.ecp_substrate import ECPSubstrate
from ecp.forgetting_engine import ForgettingEngine
from ecp.paradox_engine import ParadoxEngine
from ecp.model_bridge import ModelBridge
from tools.approval_system import ApprovalSystem

logger = logging.getLogger(__name__)

class VargasAgentV4:
    """
    Vargas V4 Unified Agent
    
    Sovereign collaborator with:
    - ECP (Emotional Calibration Protocol) integration
    - Paradox detection and E-Vector management
    - Bounded tool execution with approval gating
    - Sovereign state management
    """
    
    def __init__(self, config_dir: Path):
        """Initialize V4 agent with sovereign state and ECP components."""
        self.config_dir = config_dir
        
        # Initialize sovereign state (Phase 1)
        self.sovereign_manager = initialize_sovereign_state(config_dir)
        
        # Check if system is healthy
        if not self.sovereign_manager.is_quiescent_mode():
            logger.info("[V4] Sovereign state verified, system healthy")
        else:
            logger.warning("[V4] System in quiescent mode")
        
        # Initialize ECP components (Phase 2)
        self._initialize_ecp_components()
        
        # Initialize memory and LLM systems
        self._initialize_memory_and_llm()
        
        # Initialize tool approval system (Phase 4)
        self.approval_system = ApprovalSystem()
        
        # Agent state
        self.session_start = datetime.now(timezone.utc)
        self.interaction_count = 0
        
        logger.info("[V4] Agent initialized successfully")
    
    def _initialize_ecp_components(self):
        """Initialize ECP components with sovereign constraints."""
        # Get ECP configuration from sovereign state
        ecp_config = self.sovereign_manager.get_paradox_engine_config()
        
        # Initialize substrate with dimensions from config
        substrate_dimensions = ecp_config.get("substrate_dimensions", 384)
        base_threshold = ecp_config.get("base_threshold", 0.618)
        self.substrate = ECPSubstrate(dimensions=substrate_dimensions, base_threshold=base_threshold)
        
        # Initialize forgetting engine
        retention_threshold = ecp_config.get("retention_threshold", 0.3)
        self.forgetting_engine = ForgettingEngine(self.substrate, retention_threshold)
        
        # Initialize paradox engine with blueprint thresholds
        self.paradox_engine = ParadoxEngine(self.substrate, self.forgetting_engine)
        
        # Initialize model bridge
        self.model_bridge = ModelBridge(self.substrate, self.forgetting_engine)
        
        logger.info("[V4] ECP components initialized")
    
    def _initialize_memory_and_llm(self):
        """Initialize memory and LLM systems."""
        # Load configuration
        config_path = self.config_dir / "vargas_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Initialize LLM client
        self.llm_client = GeminiLLMClient(
            default_model=config.get("model", "gemini-2.5-pro"),
            embedding_model=config.get("embedding_model", "gemini-embedding-001"),
            fallback_model=config.get("fallback_model", "gemini-2.5-pro")
        )
        
        # Initialize memory client
        qdrant_config = config.get("qdrant", {})
        self.memory_client = VargasMemoryClient(
            qdrant_url=qdrant_config.get("url"),
            qdrant_api_key=qdrant_config.get("api_key"),
            llm_bridge=self.llm_client
        )
        
        # Initialize E-Vector system with baseline from sovereign state
        e_vector_baseline = self.sovereign_manager.get_e_vector_baseline()
        self.e_vector_system = EVectorSystem(e_vector_baseline)
        
        logger.info("[V4] Memory and LLM systems initialized")
    
    async def respond(self, user_message: str, channel_id: str, user_id: str) -> str:
        """
        Generate response to user message using V4 architecture.
        
        Args:
            user_message: User's input message
            channel_id: Discord channel ID
            user_id: Discord user ID
            
        Returns:
            Generated response
        """
        self.interaction_count += 1
        
        try:
            # Check sovereign state health
            if self.sovereign_manager.is_quiescent_mode():
                return self._generate_quiescent_response()
            
            # Phase 1: Input ingestion and metadata
            input_metadata = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "channel_id": channel_id,
                "user_id": user_id,
                "interaction_count": self.interaction_count,
                "session_age_seconds": (datetime.now(timezone.utc) - self.session_start).total_seconds()
            }
            
            # Phase 2: Context assembly (memory retrieval)
            memory_context = await self._assemble_memory_context(user_message)
            
            # Phase 3: Paradox Engine analysis
            paradox_analysis = await self._run_paradox_analysis(user_message, memory_context)
            
            # Phase 4: E-Vector state update
            e_vector_update = self._update_e_vector_state(paradox_analysis)
            
            # Phase 5: Response generation with sovereign constraints
            response = await self._generate_response(
                user_message, memory_context, paradox_analysis, e_vector_update
            )
            
            # Phase 6: Post-response memory updates
            await self._update_memory(user_message, response, input_metadata)
            
            return response
            
        except Exception as e:
            logger.error(f"[V4] Error in respond(): {e}")
            return self._generate_error_response(e)
    
    async def _assemble_memory_context(self, user_message: str) -> Dict[str, Any]:
        """Assemble memory context from all three memory classes."""
        # Retrieve relevant memories from all collections
        identity_memories = self.memory_client.retrieve(user_message, "vargas_identity", top_k=3)
        behavioral_memories = self.memory_client.retrieve(user_message, "vargas_behavioral", top_k=3)
        attunement_memories = self.memory_client.retrieve(user_message, "vargas_attunement", top_k=3)
        
        return {
            "identity": identity_memories,
            "behavioral": behavioral_memories,
            "attunement": attunement_memories,
            "total_retrieved": len(identity_memories) + len(behavioral_memories) + len(attunement_memories)
        }
    
    async def _run_paradox_analysis(self, user_message: str, memory_context: Dict[str, Any]) -> Dict[str, Any]:
        """Run paradox detection and ECP analysis."""
        # Generate embeddings for analysis
        user_embedding = self.llm_client.embed(user_message)
        
        # Check for contradictions with recent memories
        contradictions = []
        for collection in ["identity", "behavioral", "attunement"]:
            memories = memory_context.get(collection, [])
            for memory in memories:
                memory_embedding = self.llm_client.embed(memory["content"])
                
                # Detect contradiction using paradox engine
                paradox = self.paradox_engine.detect_contradiction(
                    topic_vector_a=user_embedding,
                    topic_vector_b=memory_embedding,
                    implication_vector_a=user_embedding,  # Simplified for now
                    implication_vector_b=memory_embedding,
                    source_text=f"User: {user_message} | Memory: {memory['content']}"
                )
                
                if paradox:
                    contradictions.append(paradox)
                    # Process paradox through ECP system
                    self.paradox_engine.process_paradox(paradox)
        
        # Calculate current tension
        current_tension = self.substrate.compute_tension_gradient(
            user_embedding, self.substrate.state_vector
        )
        
        return {
            "contradictions_detected": len(contradictions),
            "contradictions": contradictions,
            "current_tension": current_tension,
            "substrate_state": self.substrate.summary(),
            "engine_state": self.forgetting_engine.summary()
        }
    
    def _update_e_vector_state(self, paradox_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Update E-Vector state based on paradox analysis."""
        # Calculate E-Vector delta from paradox analysis
        delta = {}
        
        if paradox_analysis["contradictions_detected"] > 0:
            # Increase entropy and chaos thresholds based on contradictions
            delta["entropy_level"] = 0.1 * min(paradox_analysis["contradictions_detected"], 3)
            delta["chaos_threshold"] = 0.15 * min(paradox_analysis["contradictions_detected"], 3)
            delta["challenge_threshold"] = 0.05 * min(paradox_analysis["contradictions_detected"], 3)
        
        # Apply delta if present
        if delta:
            self.e_vector_system.apply_delta(delta, "paradox_analysis")
        
        return {
            "delta_applied": delta,
            "new_state": self.e_vector_system.get_current_state().to_dict(),
            "distance_from_baseline": self.e_vector_system.calculate_distance_from_baseline()
        }
    
    async def _generate_response(
        self,
        user_message: str,
        memory_context: Dict[str, Any],
        paradox_analysis: Dict[str, Any],
        e_vector_update: Dict[str, Any]
    ) -> str:
        """Generate response with sovereign constraints."""
        # Get sovereign constraints
        tone_rules = self.sovereign_manager.get_tone_rules()
        challenge_ethics = self.sovereign_manager.get_challenge_ethics()
        
        # Build system prompt with V4 identity and ECP context
        system_prompt = self._build_system_prompt(tone_rules, challenge_ethics, e_vector_update)
        
        # Build user prompt with context
        user_prompt = self._build_user_prompt(user_message, memory_context, paradox_analysis)
        
        # Generate response
        response = self.llm_client.generate(
            model=self.llm_client.default_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temp=0.7,
            max_tokens=2048
        )
        
        # Apply sovereign constraints to response
        return self._apply_sovereign_constraints(response, tone_rules)
    
    def _build_system_prompt(
        self,
        tone_rules: Dict[str, Any],
        challenge_ethics: Dict[str, Any],
        e_vector_update: Dict[str, Any]
    ) -> str:
        """Build system prompt with V4 identity and current state."""
        # Load base system prompt
        prompt_path = self.config_dir / "prompts" / "system_prompt.md"
        with open(prompt_path, 'r') as f:
            base_prompt = f.read()
        
        # Add current E-Vector state
        e_vector_state = e_vector_update["new_state"]
        e_vector_context = f"""
CURRENT E-VECTOR STATE:
- Entropy Level: {e_vector_state['entropy_level']:.3f} (complexity tolerance)
- Chaos Threshold: {e_vector_state['chaos_threshold']:.3f} (contradiction tolerance)
- Challenge Threshold: {e_vector_state['challenge_threshold']:.3f} (intervention readiness)
- Initiative Timer: {e_vector_state['initiative_timer']:.1f}s (action timing)

Distance from baseline: {e_vector_update['distance_from_baseline']:.3f}
"""
        
        return base_prompt + "\n\n" + e_vector_context
    
    def _build_user_prompt(
        self,
        user_message: str,
        memory_context: Dict[str, Any],
        paradox_analysis: Dict[str, Any]
    ) -> str:
        """Build user prompt with memory context and analysis."""
        prompt_parts = [f"User message: {user_message}\n"]
        
        # Add memory context
        if memory_context["total_retrieved"] > 0:
            prompt_parts.append("\nRelevant memories:")
            for collection in ["identity", "behavioral", "attunement"]:
                memories = memory_context.get(collection, [])
                if memories:
                    prompt_parts.append(f"\n{collection.capitalize()}:")
                    for memory in memories[:2]:  # Limit to top 2 per collection
                        prompt_parts.append(f"- {memory['content']}")
        
        # Add paradox analysis
        if paradox_analysis["contradictions_detected"] > 0:
            prompt_parts.append(f"\nParadox analysis: {paradox_analysis['contradictions_detected']} contradictions detected")
            prompt_parts.append(f"Current tension: {paradox_analysis['current_tension']:.3f}")
        
        return "\n".join(prompt_parts)
    
    def _apply_sovereign_constraints(self, response: str, tone_rules: Dict[str, Any]) -> str:
        """Apply sovereign tone constraints to response."""
        # Remove exclamation points if prohibited
        if tone_rules.get("no_exclamation_points", True):
            response = response.replace("!", ".")
        
        # Remove therapeutic language patterns
        if tone_rules.get("no_therapeutic_language", True):
            therapeutic_patterns = [
                "I understand how you feel",
                "It's okay to feel",
                "Take care of yourself",
                "Remember to be kind to yourself"
            ]
            for pattern in therapeutic_patterns:
                response = response.replace(pattern, "")
        
        # Ensure response ends with proper punctuation
        response = response.strip()
        if response and not response.endswith((".", "?", ":", ";")):
            response += "."
        
        return response
    
    async def _update_memory(self, user_message: str, response: str, metadata: Dict[str, Any]):
        """Update memory with interaction data."""
        # Store interaction as behavioral memory
        interaction_content = f"User: {user_message}\nV4: {response}"
        self.memory_client.store(
            collection="vargas_behavioral",
            content=interaction_content,
            memory_type="observed_pattern",
            confidence=0.8,
            rationale="Interaction pattern for continuity tracking",
            metadata=metadata
        )
        
        # Check if explicit memory commands are present
        await self._process_memory_commands(user_message, metadata)
    
    async def _process_memory_commands(self, user_message: str, metadata: Dict[str, Any]):
        """Process explicit memory commands (!forget, !correct, !query_memory)."""
        message_lower = user_message.lower().strip()
        
        if message_lower.startswith("!forget"):
            # Handle forget command
            parts = message_lower.split(" ", 1)
            if len(parts) > 1:
                content_to_forget = parts[1]
                # Search for matching memories and forget them
                memories = self.memory_client.retrieve(content_to_forget)
                forgotten_count = 0
                for memory in memories[:3]:  # Limit to top 3 matches
                    if self.memory_client.forget(memory["id"], memory["collection"]):
                        forgotten_count += 1
                logger.info(f"[V4] Forgot {forgotten_count} memories matching: {content_to_forget}")
        
        elif message_lower.startswith("!correct"):
            # Handle correction command
            parts = message_lower.split(" ", 2)
            if len(parts) > 2:
                memory_type = parts[1]
                correction_content = parts[2]
                if self.memory_client.validate_explicit_memory(memory_type, correction_content):
                    self.memory_client.store_explicit(memory_type, correction_content, metadata)
                    logger.info(f"[V4] Stored explicit correction: {memory_type}")
        
        elif message_lower.startswith("!query_memory"):
            # Handle memory query command
            parts = message_lower.split(" ", 1)
            if len(parts) > 1:
                query = parts[1]
                memories = self.memory_client.retrieve(query, top_k=5)
                memory_summary = "\n".join([f"- {m['content']}" for m in memories])
                logger.info(f"[V4] Memory query results: {memory_summary}")
    
    def _generate_quiescent_response(self) -> str:
        """Generate response when in quiescent mode."""
        return "System is currently operating in limited mode. Sovereign state verification failed."
    
    def _generate_error_response(self, error: Exception) -> str:
        """Generate error response following sovereign protocol."""
        return "I encountered an error processing your request. The issue has been logged for review."
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "sovereign_state": self.sovereign_manager.get_quiescent_status(),
            "ecp_components": {
                "substrate": self.substrate.summary(),
                "forgetting_engine": self.forgetting_engine.summary(),
                "paradox_engine": self.paradox_engine.get_paradox_statistics(),
                "model_bridge": self.model_bridge.summary() if hasattr(self.model_bridge, 'summary') else {}
            },
            "e_vector": self.e_vector_system.get_state_summary(),
            "memory": self.memory_client.health_check(),
            "approval_system": self.approval_system.get_system_status(),
            "session": {
                "start_time": self.session_start.isoformat(),
                "interaction_count": self.interaction_count,
                "session_age_seconds": (datetime.now(timezone.utc) - self.session_start).total_seconds()
            }
        }
    
    def close(self):
        """Close agent and cleanup resources."""
        self.llm_client.close()
        logger.info("[V4] Agent closed")
