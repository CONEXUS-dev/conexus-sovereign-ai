"""
Project Vargas — Core Agent V4 with ECP Integration

V4 adds Emotional Calibration Protocol (ECP) architecture to V3:
- 80% context window tripwire for autonomous memory compression
- Dual-vector interception for model outputs (consensus=DELETE, tension=SURVIVE)
- Recursive reinjection of surviving paradoxes
- Sovereign memory preservation with tension metrics

Single entry point: respond(user_message, channel_id) -> str

Enhanced Flow:
  1. Load conversation history for channel
  2. Read memory (all 3 classes) -> build memory context
  3. Run intent classifier
  4. ECP Tripwire Check: If context > 80%, trigger autonomous compression
  5. If web_search -> fetch results -> inject into prompt
  6. If skill_invoke -> match skill -> inject skill body into prompt
  7. If memory_inspect -> format memory summary -> inject into prompt
  8. If memory_modify -> execute modification -> confirm naturally
  9. Build system prompt + memory context + tool results + conversation history
 10. Call Gemini 3.1 Pro through ECP interceptor
 11. Post-response: evaluate for memory write triggers + ECP processing
 12. Return response text
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Original V3 imports - adjusted for relative imports
try:
    from adapters.cloud_llm.gemini_client import GeminiLLMClient
    from memory.memory_client import VargasMemoryClient
    from memory.emoji.emoji_vector import EmojiVector
    from memory.emoji.emoji_mutator import seed_initial_sequence, mutate_for_operator
    from agent.intent_classifier import classify_intent
    from tools.web_search import WebSearchTool
    from tools.url_reader import URLReaderTool
    from tools.openclaw_bridge import OpenClawBridge
    from tools.executor import ToolExecutor, ToolCall, SafetyLevel
    from tools.browser import BrowserTool
    from tools.shell import ShellTool
    from tools.file_io import FileIOTool
    from agent.agent_loop import AgentLoop
    from adapters.sovereign_bridge import SovereignBridge
except ImportError:
    # Fallback for standalone testing
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning("[V4] Some V3 components not available - running in test mode")
    GeminiLLMClient = None
    VargasMemoryClient = None
    EmojiVector = None
    classify_intent = None
    WebSearchTool = None
    URLReaderTool = None
    OpenClawBridge = None
    ToolExecutor = None
    BrowserTool = None
    ShellTool = None
    FileIOTool = None
    AgentLoop = None
    SovereignBridge = None

# V4 ECP imports
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent / "ecp"))

from ecp_substrate import ECPSubstrate
from forgetting_engine import ForgettingEngine
from model_bridge import ModelBridge
from memory_compression import TensionCompressor
from recursive_reinjection import RecursiveReinjection

logger = logging.getLogger(__name__)

# Load system prompt from file
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system_prompt.md"
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "vargas_config.json"
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"

# ECP Configuration
ECP_CONTEXT_THRESHOLD = 0.80  # 80% context window tripwire
ECP_MAX_TOKENS = 128000  # Approximate max context for Gemini 1.5 Pro
TOKENS_PER_CHAR = 0.25  # Rough estimate


class VargasAgentV4:
    """Vargas Agent V4 with Emotional Calibration Protocol integration"""
    
    def __init__(self):
        # Original V3 initialization
        if GeminiLLMClient is not None:
            self.llm_client = GeminiLLMClient()
        else:
            self.llm_client = None
            
        if VargasMemoryClient is not None:
            self.memory_client = VargasMemoryClient()
        else:
            self.memory_client = None
            
        self.emoji_vector = EmojiVector() if EmojiVector is not None else None
        self.web_search = WebSearchTool() if WebSearchTool is not None else None
        self.url_reader = URLReaderTool() if URLReaderTool is not None else None
        self.openclaw_bridge = OpenClawBridge() if OpenClawBridge is not None else None
        self.tool_executor = ToolExecutor() if ToolExecutor is not None else None
        self.browser = BrowserTool() if BrowserTool is not None else None
        self.shell = ShellTool() if ShellTool is not None else None
        self.file_io = FileIOTool() if FileIOTool is not None else None
        self.agent_loop = AgentLoop() if AgentLoop is not None else None
        self.sovereign_bridge = SovereignBridge() if SovereignBridge is not None else None
        
        # V4 ECP components
        self.substrate = ECPSubstrate(dimensions=384, base_threshold=0.618)
        self.forgetting_engine = ForgettingEngine(self.substrate, retention_threshold=0.3)
        self.model_bridge = ModelBridge(self.substrate, self.forgetting_engine)
        self.memory_compressor = TensionCompressor(self.substrate, retention_threshold=0.75)
        self.reinjector = RecursiveReinjection(self.substrate, self.forgetting_engine, self.model_bridge)
        
        # ECP state tracking
        self.context_tokens_used = 0
        self.last_compression_time = datetime.now(timezone.utc)
        self.compression_interval_hours = 1  # Compress at most once per hour
        
        logger.info("[V4] Vargas Agent V4 initialized with ECP architecture")
        logger.info("[V4] ECP components: substrate, engine, bridge, compressor, reinjector")
    
    def estimate_token_count(self, text: str) -> int:
        """Rough token estimation for tripwire calculation"""
        return int(len(text) * TOKENS_PER_CHAR)
    
    def calculate_context_usage(self, conversation_history: List[Dict], memory_context: str, system_prompt: str) -> float:
        """Calculate current context usage as percentage of maximum"""
        total_text = system_prompt + memory_context
        
        # Add conversation history
        for msg in conversation_history:
            if isinstance(msg, dict) and 'content' in msg:
                total_text += msg['content']
        
        estimated_tokens = self.estimate_token_count(total_text)
        usage_percentage = estimated_tokens / ECP_MAX_TOKENS
        
        return usage_percentage
    
    def check_ecp_tripwire(self, conversation_history: List[Dict], memory_context: str, system_prompt: str) -> bool:
        """Check if 80% context tripwire is triggered"""
        usage_percentage = self.calculate_context_usage(conversation_history, memory_context, system_prompt)
        
        if usage_percentage >= ECP_CONTEXT_THRESHOLD:
            logger.warning(f"[V4] ECP Tripwire triggered: {usage_percentage:.1%} context usage")
            return True
        
        return False
    
    def trigger_autonomous_compression(self, channel_id: str) -> Dict[str, Any]:
        """Trigger autonomous memory compression when tripwire is hit"""
        logger.info("[V4] Triggering autonomous memory compression")
        
        # Check compression cooldown
        time_since_last = (datetime.now(timezone.utc) - self.last_compression_time).total_seconds()
        cooldown_seconds = self.compression_interval_hours * 3600
        
        if time_since_last < cooldown_seconds:
            logger.info(f"[V4] Compression in cooldown ({time_since_last:.0f}s < {cooldown_seconds}s)")
            return {"status": "skipped", "reason": "cooldown"}
        
        try:
            # Get recent conversation history for compression
            history = self.memory_client.get_conversation_history(channel_id, limit=50)
            
            if not history:
                logger.info("[V4] No conversation history to compress")
                return {"status": "skipped", "reason": "no_history"}
            
            # Extract memory blocks and calculate tension scores
            memory_blocks = []
            tension_scores = []
            
            for msg in history:
                if isinstance(msg, dict) and 'content' in msg:
                    content = msg['content']
                    memory_blocks.append(content)
                    
                    # Calculate tension score using ECP substrate
                    embedding = self.model_bridge.embed(content)
                    tension = self.substrate.compute_tension_gradient(embedding, self.substrate.state_vector)
                    tension_scores.append(tension)
            
            # Run compression cycle
            compression_result = self.memory_compressor.autonomous_compression_cycle(memory_blocks)
            
            # Write compressed payload to memory
            payload = self.memory_compressor.create_compression_payload(compression_result)
            
            # Store compression record in memory
            compression_record = {
                "type": "ecp_compression",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "channel_id": channel_id,
                "compression_ratio": compression_result["compression_ratio"],
                "tension_preservation": compression_result["tension_preservation"],
                "blocks_processed": len(memory_blocks),
                "substrate_state": self.substrate.summary()
            }
            
            self.memory_client.write_memory(
                channel_id=channel_id,
                memory_type="behavioral",
                content=json.dumps(compression_record),
                metadata={"event": "ecp_compression", "autonomous": True}
            )
            
            # Update last compression time
            self.last_compression_time = datetime.now(timezone.utc)
            
            logger.info(f"[V4] Compression complete: ratio={compression_result['compression_ratio']:.2f}, "
                       f"tension_preserved={compression_result['tension_preservation']:.2f}")
            
            return {
                "status": "completed",
                "compression_ratio": compression_result["compression_ratio"],
                "tension_preservation": compression_result["tension_preservation"],
                "blocks_processed": len(memory_blocks)
            }
            
        except Exception as e:
            logger.error(f"[V4] Compression failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def process_model_output_through_ecp(self, prompt: str, response: str, channel_id: str) -> str:
        """Process model output through ECP interceptor and store results"""
        try:
            # Run through model bridge for dual-vector evaluation
            processed_response, passes = self.model_bridge.process_model_output(prompt, response)
            
            if passes:
                # Response passed dual-vector test - store in ECP system
                logger.debug("[V4] Response passed ECP dual-vector test")
                
                # Process through forgetting engine
                response_embedding = self.model_bridge.embed(processed_response)
                self.forgetting_engine.process_signal(response_embedding)
                
                # Extract paradoxes for substrate
                paradoxes = self.model_bridge.extract_paradoxes(processed_response)
                for paradox in paradoxes:
                    paradox_embedding = self.model_bridge.embed(paradox)
                    self.substrate.preserve_paradox(paradox_embedding)
                
                # Store ECP metrics in memory
                ecp_metrics = {
                    "type": "ecp_processing",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "channel_id": channel_id,
                    "prompt_length": len(prompt),
                    "response_length": len(processed_response),
                    "substrate_metrics": self.substrate.summary(),
                    "engine_metrics": self.forgetting_engine.summary(),
                    "paradoxes_extracted": len(paradoxes)
                }
                
                self.memory_client.write_memory(
                    channel_id=channel_id,
                    memory_type="behavioral",
                    content=json.dumps(ecp_metrics),
                    metadata={"event": "ecp_processing", "response_passed": True}
                )
                
                return processed_response
            else:
                # Response failed - log the failure
                logger.warning("[V4] Response failed ECP dual-vector test")
                
                failure_record = {
                    "type": "ecp_processing",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "channel_id": channel_id,
                    "prompt_length": len(prompt),
                    "response_length": len(response),
                    "status": "failed_dual_vector_test",
                    "substrate_metrics": self.substrate.summary()
                }
                
                self.memory_client.write_memory(
                    channel_id=channel_id,
                    memory_type="behavioral",
                    content=json.dumps(failure_record),
                    metadata={"event": "ecp_processing", "response_passed": False}
                )
                
                return response  # Return original response if it fails
                
        except Exception as e:
            logger.error(f"[V4] ECP processing failed: {e}")
            return response
    
    async def respond(self, user_message: str, channel_id: str) -> str:
        """Main response method with ECP integration"""
        try:
            # Load conversation history
            conversation_history = self.memory_client.get_conversation_history(channel_id)
            
            # Read memory and build context
            memory_context = await self._build_memory_context(user_message, channel_id)
            
            # Load system prompt
            system_prompt = self._load_system_prompt()
            
            # Check ECP tripwire
            if self.check_ecp_tripwire(conversation_history, memory_context, system_prompt):
                compression_result = self.trigger_autonomous_compression(channel_id)
                logger.info(f"[V4] Compression result: {compression_result['status']}")
            
            # Run intent classifier
            intent = await self._classify_intent(user_message, channel_id)
            
            # Process intent-based actions
            tool_results = await self._process_intent(intent, user_message, channel_id)
            
            # Build full prompt
            full_prompt = self._build_prompt(system_prompt, memory_context, tool_results, conversation_history, user_message)
            
            # Generate response through LLM
            raw_response = await self.llm_client.generate(full_prompt)
            
            # Process through ECP interceptor
            processed_response = self.process_model_output_through_ecp(full_prompt, raw_response, channel_id)
            
            # Post-response memory operations
            await self._post_response_processing(processed_response, user_message, channel_id, intent)
            
            return processed_response
            
        except Exception as e:
            logger.error(f"[V4] Response generation failed: {e}")
            return "I encountered an error processing your request. Please try again."
    
    async def _build_memory_context(self, user_message: str, channel_id: str) -> str:
        """Build memory context (original V3 method)"""
        # This would contain the original V3 memory building logic
        # For now, return placeholder
        return f"[Memory context for channel {channel_id}]"
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from file"""
        try:
            with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("System prompt file not found, using default")
            return "You are Vargas, a sovereign AI collaborator."
    
    async def _classify_intent(self, user_message: str, channel_id: str) -> Dict[str, Any]:
        """Classify user intent (original V3 method)"""
        return classify_intent(user_message, channel_id)
    
    async def _process_intent(self, intent: Dict[str, Any], user_message: str, channel_id: str) -> str:
        """Process intent-based actions (original V3 method)"""
        # This would contain the original V3 intent processing logic
        # For now, return placeholder
        return "[Tool results placeholder]"
    
    def _build_prompt(self, system_prompt: str, memory_context: str, tool_results: str, 
                     conversation_history: List[Dict], user_message: str) -> str:
        """Build the complete prompt for LLM"""
        # This would contain the original V3 prompt building logic
        # For now, return simple combination
        return f"{system_prompt}\n\n{memory_context}\n\n{tool_results}\n\nUser: {user_message}"
    
    async def _post_response_processing(self, response: str, user_message: str, 
                                       channel_id: str, intent: Dict[str, Any]) -> None:
        """Post-response processing (original V3 method)"""
        # This would contain the original V3 post-response logic
        pass
    
    def get_ecp_status(self) -> Dict[str, Any]:
        """Get current ECP system status"""
        return {
            "substrate": self.substrate.summary(),
            "forgetting_engine": self.forgetting_engine.summary(),
            "context_usage": f"{self.calculate_context_usage([], '', ''):.1%}",
            "last_compression": self.last_compression_time.isoformat(),
            "compression_cooldown_hours": self.compression_interval_hours
        }
    
    def run_recursive_cycle(self, seed: str, num_cycles: int = 3) -> Dict[str, Any]:
        """Run recursive reinjection cycle for testing"""
        def mock_model_generate(prompt: str) -> str:
            return f"Mock response to seed: {seed[:50]}..."
        
        return self.reinjector.run_recursive_cycle(seed, num_cycles, mock_model_generate)


# Factory function for easy instantiation
def create_vargas_agent_v4() -> VargasAgentV4:
    """Create and return a Vargas Agent V4 instance"""
    return VargasAgentV4()


# Backward compatibility - maintain V3 interface
def create_vargas_agent() -> VargasAgentV4:
    """Create Vargas agent (now V4 with ECP)"""
    return create_vargas_agent_v4()
