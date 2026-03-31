"""
VARGAS V4 Sovereign Perception Loop — Central Nervous System

The SovereignPerceptionLoop is the orchestrator that integrates all VARGAS V4
components into a unified intelligence system. It executes the complete
perception-to-action sequence for every message, maintaining the system's
sovereign posture while detecting and responding to contradictions.

Architecture Flow:
    Perception → Evaluation → Posture Shift → Gating → Logging → Output

Components Integrated:
    - Memory Client (The Brain): Context retrieval from ECP stores
    - Paradox Engine (The Heart): Contradiction detection and delta computation
    - E-Vector Controller (The Posture): System posture management
    - Action Router (The Muscle): Trust-tiered action gating
    - Provenance Logger (The Record): Immutable audit trail

The Perception Loop never modifies the core components directly. It uses their
public APIs as intended by the Architect, preserving the clean separation
of concerns established in Phases 2-5.
"""

import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
load_dotenv()

from adapters.cloud_llm.gemini_client import GeminiLLMClient
from memory.memory_client import ECPMemoryClient
from memory.memory_summarizer import MemorySummarizer
from paradox.paradox_engine import ParadoxEngine, RESOLUTION_GATE, WITNESS_MODE
from paradox.e_vector_controller import EVectorController
from paradox.contradiction_detector import ContradictionDetector
from paradox.challenge_engine import ChallengeEngine
from paradox.resolution_gate import ResolutionGate
from tools.action_router import ActionRouter
from tools.executor import ToolExecutor
from provenance.provenance_chain import ProvenanceLogger
from provenance.action_log import ActionLog
from provenance.memory_log import MemoryLog
from provenance.integrity_log import IntegrityLog
from safety.trust_model import TrustModel
from safety.forbidden_ops import ForbiddenOps
from safety.rollback_engine import RollbackEngine
from safety.escalation_manager import EscalationManager
from agent.intent_router import IntentRouter
from agent.state_controller import StateController
from agent.plan_manager import PlanManager

logger = logging.getLogger(__name__)


class SovereignPerceptionLoop:
    """
    Central nervous system of VARGAS V4 sovereign runtime.
    
    Orchestrates the complete perception-to-action sequence while maintaining
    system integrity through trust-tiered gating and provenance logging.
    """
    
    def __init__(self, config_path: str = "config/sovereign_state.json"):
        """Initialize the Perception Loop with all component dependencies.
        
        Args:
            config_path: Path to sovereign_state.json configuration.
        """
        self.config_path = config_path
        self.session_id = str(uuid.uuid4())
        self.session_start = datetime.now(timezone.utc)
        
        # Initialize LLM client (Gemini) — needed for embeddings and response generation
        self.llm = None
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                self.llm = GeminiLLMClient(
                    api_key=gemini_key,
                    default_model="gemini-2.5-flash",
                    fallback_model="gemini-2.0-flash",
                )
                logger.info("[PERCEPTION_LOOP] Gemini LLM client initialized")
            except Exception as e:
                logger.warning("[PERCEPTION_LOOP] Gemini init failed: %s — using fallback voice", e)
        else:
            logger.warning("[PERCEPTION_LOOP] No GEMINI_API_KEY — using fallback voice")
        
        # Initialize core components (The Architect's domain)
        self.memory_client = ECPMemoryClient(
            qdrant_url=os.getenv("QDRANT_URL"),
            qdrant_api_key=os.getenv("QDRANT_API_KEY"),
            llm_bridge=self.llm,
        )
        self.memory_summarizer = MemorySummarizer()
        self.paradox_engine = ParadoxEngine(config_path=config_path)
        self.e_vector_controller = EVectorController(config_path=config_path)
        
        # Initialize paradox pipeline
        self.contradiction_detector = ContradictionDetector()
        self.challenge_engine = ChallengeEngine()
        self.resolution_gate = ResolutionGate()
        
        # Initialize agent core
        self.intent_router = IntentRouter()
        self.state_controller = StateController(
            session_id=self.session_id, boot_mode="NORMAL"
        )
        self.plan_manager = PlanManager()
        
        # Initialize safety layer
        self.trust_model = TrustModel(max_allowed_tier=3)
        self.forbidden_ops = ForbiddenOps()
        self.rollback_engine = RollbackEngine()
        self.escalation_manager = EscalationManager()
        
        # Initialize tool executor
        self.tool_executor = ToolExecutor(max_allowed_tier=3)
        
        # Initialize infrastructure components
        self.action_router = ActionRouter(config_path=config_path)
        self.provenance_logger = ProvenanceLogger(session_id=self.session_id)
        self.action_log = ActionLog(session_id=self.session_id)
        self.memory_log = MemoryLog(session_id=self.session_id)
        self.integrity_log = IntegrityLog()
        
        # Seed bootstrap truths — system must know who it is and who it serves
        self._seed_bootstrap_truths()
        
        # Initialize voice signature (Partner Stance calibration)
        from symbolic.voice_signature import VoiceSignature
        self.voice_signature = VoiceSignature(self._load_sovereign_config())
        
        logger.info(
            "[PERCEPTION_LOOP] Initialized: session_id=%s config=%s",
            self.session_id,
            config_path,
        )
    
    def process_message(
        self,
        message: str,
        action_request: Optional[Dict[str, Any]] = None,
        context_limit: int = 5,
    ) -> Dict[str, Any]:
        """
        Execute the complete perception loop for a single message.
        
        Args:
            message: Input message to process.
            action_request: Optional action to evaluate and potentially execute.
            context_limit: Maximum context items to retrieve from memory.
            
        Returns:
            Dict containing:
                - response_text: Generated response
                - system_state: Updated E-Vector and trust information
                - contradiction_info: Details if contradiction detected
                - action_result: Result of action routing if action provided
                - provenance_entry: Complete audit trail entry
        """
        loop_start = datetime.now(timezone.utc)
        turn_number = self.state_controller.begin_turn()
        
        try:
            # Step 0: Intent Classification
            logger.info("[PERCEPTION_LOOP] Step 0: Intent classification")
            intent_result = self.intent_router.classify(message)
            self.state_controller.update_intent(intent_result["intent"])
            
            # Step 1: Perception - Retrieve context from ECP memory
            logger.info("[PERCEPTION_LOOP] Step 1: Perception - Retrieving context")
            context = self._retrieve_context(message, context_limit)
            
            # Step 2: Evaluation - Paradox Engine + Contradiction Detector
            logger.info("[PERCEPTION_LOOP] Step 2: Evaluation - Paradox pipeline")
            paradox_result = self._evaluate_contradiction(message, context)
            
            # Step 2a: Run contradiction detector for new contradictions
            new_contradictions = self.contradiction_detector.detect(
                message, context.get("truth", []), context.get("contradiction", [])
            )
            
            # Step 2b: Evaluate challenges if contradictions warrant it
            challenge_result = None
            if new_contradictions or paradox_result.get("state") == RESOLUTION_GATE:
                challenges = self.challenge_engine.batch_evaluate(
                    [c.to_dict() for c in new_contradictions],
                    self.e_vector_controller.get_current_posture(),
                    context.get("truth", []),
                )
                if challenges:
                    challenge_result = challenges[0]
            
            # Step 2c: Resolution Gate management
            if paradox_result.get("state") == RESOLUTION_GATE:
                if not self.resolution_gate.is_active():
                    self.resolution_gate.activate(
                        contradiction=paradox_result,
                        severity=paradox_result.get("severity_score", 0.0),
                    )
                    self.trust_model.set_contradiction_escalation(True)
            elif self.resolution_gate.is_active():
                self.resolution_gate.resolve(resolution="contradiction_cleared")
                self.trust_model.set_contradiction_escalation(False)
            
            # Update state controller with contradiction state
            self.state_controller.update_contradiction_state(
                state=paradox_result.get("state", WITNESS_MODE),
                active_count=paradox_result.get("active_contradictions", 0),
                severity=paradox_result.get("severity_score", 0.0),
            )
            
            # Step 3: Posture Shift - Apply E-Vector deltas if needed
            logger.info("[PERCEPTION_LOOP] Step 3: Posture Shift - Applying deltas")
            posture_result = self._apply_posture_shift(paradox_result)
            self.state_controller.update_posture(
                self.e_vector_controller.get_current_posture()
            )
            
            # Step 4: Gating - Route action through Trust Spine
            logger.info("[PERCEPTION_LOOP] Step 4: Gating - Action Router evaluation")
            action_result = self._route_action(action_request, paradox_result)
            
            # Log action to provenance
            if action_result:
                self.action_log.log_execution(
                    tool_name=action_result.get("action", {}).get("action_type", "unknown"),
                    status=action_result.get("status", "unknown"),
                    trust_tier=action_result.get("trust_tier", 0),
                    parameters=action_result.get("action", {}),
                    result=action_result,
                )
            
            # Step 5: Logging - Record complete transition
            logger.info("[PERCEPTION_LOOP] Step 5: Logging - Provenance recording")
            provenance_entry = self._log_transition(
                message, context, paradox_result, posture_result, action_result
            )
            
            # Step 6: Output - Generate structured response
            logger.info("[PERCEPTION_LOOP] Step 6: Output - Response generation")
            response = self._generate_response(message, paradox_result, posture_result)
            
            # Compile complete result
            result = {
                "session_id": self.session_id,
                "turn_number": turn_number,
                "loop_timestamp": loop_start.isoformat(),
                "message": message,
                "intent": intent_result,
                "response_text": response,
                "system_state": {
                    "e_vector": self.e_vector_controller.get_current_posture(),
                    "boot_mode": self.state_controller.boot_mode,
                    "trust_tier_active": action_result.get("trust_tier") if action_result else None,
                    "execution_status": action_result.get("status") if action_result else None,
                    "resolution_gate_active": self.resolution_gate.is_active(),
                },
                "contradiction_info": {
                    "detected": paradox_result.get("state") == RESOLUTION_GATE,
                    "state": paradox_result.get("state"),
                    "severity": paradox_result.get("severity_score", 0.0),
                    "topic_similarity": paradox_result.get("topic_similarity", 0.0),
                    "implication_similarity": paradox_result.get("implication_similarity", 0.0),
                    "e_vector_delta": paradox_result.get("e_vector_delta"),
                    "new_contradictions": len(new_contradictions),
                    "challenge": challenge_result,
                },
                "action_result": action_result,
                "provenance_entry": provenance_entry,
                "processing_time_ms": int(
                    (datetime.now(timezone.utc) - loop_start).total_seconds() * 1000
                ),
            }
            
            logger.info(
                "[PERCEPTION_LOOP] Complete: turn=%d intent=%s state=%s severity=%.3f status=%s",
                turn_number,
                intent_result["intent"],
                paradox_result.get("state"),
                paradox_result.get("severity_score", 0.0),
                action_result.get("status") if action_result else "no_action",
            )
            
            return result
            
        except Exception as e:
            logger.error("[PERCEPTION_LOOP] Error in perception loop: %s", str(e))
            return {
                "session_id": self.session_id,
                "loop_timestamp": loop_start.isoformat(),
                "message": message,
                "response_text": "I encountered an error processing your message.",
                "system_state": {"error": str(e)},
                "contradiction_info": {"detected": False, "error": str(e)},
                "action_result": None,
                "provenance_entry": None,
                "processing_time_ms": int(
                    (datetime.now(timezone.utc) - loop_start).total_seconds() * 1000
                ),
            }
    
    def _retrieve_context(self, message: str, limit: int) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieve relevant context from all three ECP memory stores.
        
        The system must know who it is talking to, what was previously
        established, and what tensions are active before synthesizing a word.
        
        Args:
            message: Input message to use as query.
            limit: Maximum results per collection.
            
        Returns:
            Dict with 'truth', 'symbol', and 'contradiction' context lists.
        """
        context = {"truth": [], "symbol": [], "contradiction": []}
        
        try:
            # Retrieve from ecp_truth collection
            truth_results = self.memory_client.retrieve(
                query=message,
                collection="ecp_truth",
                top_k=limit,
                filter_status="active",
            )
            context["truth"] = truth_results[:limit]
            
            # Retrieve from ecp_symbol collection
            symbol_results = self.memory_client.retrieve(
                query=message,
                collection="ecp_symbol",
                top_k=limit,
                filter_status="active",
            )
            context["symbol"] = symbol_results[:limit]
            
            # Retrieve from ecp_contradiction collection — active tensions
            contradiction_results = self.memory_client.retrieve(
                query=message,
                collection="ecp_contradiction",
                top_k=limit,
                filter_status="active",
            )
            context["contradiction"] = contradiction_results[:limit]
            
            logger.info(
                "[PERCEPTION_LOOP] Context retrieved: %d truth, %d symbol, %d contradiction items",
                len(context["truth"]),
                len(context["symbol"]),
                len(context["contradiction"]),
            )
            
        except Exception as e:
            logger.warning("[PERCEPTION_LOOP] Context retrieval failed: %s", str(e))
            # Continue with empty context - system should be resilient
        
        return context
    
    def _evaluate_contradiction(
        self, message: str, context: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Evaluate message for contradictions using Paradox Engine.
        
        Ingests ecp_contradiction context retrieved during perception,
        computes aggregate severity from stored contradiction payloads,
        and triggers RESOLUTION_GATE when severity crosses threshold.
        
        Args:
            message: Input message to evaluate.
            context: Retrieved context from memory (must include 'contradiction' key).
            
        Returns:
            Paradox Engine evaluation result with e_vector_delta if triggered.
        """
        try:
            contradictions = context.get("contradiction", [])
            truths = context.get("truth", [])
            
            # Aggregate severity from active contradiction payloads
            max_severity = 0.0
            max_topic_sim = 0.0
            max_impl_sim = 1.0
            avg_confidence = 0.0
            active_count = 0
            
            for c in contradictions:
                content = c.get("content", "")
                # Contradiction payloads are stored as JSON strings
                try:
                    payload = json.loads(content) if isinstance(content, str) else content
                except (json.JSONDecodeError, TypeError):
                    payload = {}
                
                if payload.get("status") != "active":
                    continue
                
                active_count += 1
                sev = float(payload.get("severity_score", 0.0))
                t_sim = float(payload.get("topic_similarity", 0.0) or 0.0)
                i_sim = float(payload.get("implication_similarity", 1.0) or 1.0)
                
                if sev > max_severity:
                    max_severity = sev
                    max_topic_sim = t_sim
                    max_impl_sim = i_sim
                
                avg_confidence += float(c.get("confidence", 0.5))
            
            if active_count > 0:
                avg_confidence /= active_count
            else:
                avg_confidence = 0.0
            
            # Compute truth alignment confidence
            truth_confidence = 0.0
            if truths:
                truth_confidence = sum(
                    float(t.get("confidence", 0.5)) for t in truths
                ) / len(truths)
            
            # Apply the Logic Gate via ParadoxEngine thresholds
            is_contradiction = (
                max_topic_sim > self.paradox_engine.topic_similarity_min
                and max_impl_sim < self.paradox_engine.implication_similarity_max
            )
            
            # Also trigger if aggregate severity from stored contradictions is high
            if not is_contradiction and max_severity > 0.6:
                is_contradiction = True
            
            state = RESOLUTION_GATE if is_contradiction else WITNESS_MODE
            
            result: Dict[str, Any] = {
                "state": state,
                "topic_similarity": round(max_topic_sim, 6),
                "implication_similarity": round(max_impl_sim, 6),
                "severity_score": round(max_severity, 6),
                "active_contradictions": active_count,
                "avg_contradiction_confidence": round(avg_confidence, 6),
                "truth_confidence": round(truth_confidence, 6),
                "thresholds": {
                    "topic_similarity_min": self.paradox_engine.topic_similarity_min,
                    "implication_similarity_max": self.paradox_engine.implication_similarity_max,
                },
            }
            
            if is_contradiction:
                # Compute base E-Vector delta from severity
                base_delta = self.paradox_engine.calculate_e_vector_delta(max_severity)
                # Adjust for confidence
                adjusted_delta = self._compute_confidence_adjusted_delta(
                    base_delta, max_severity, avg_confidence, truth_confidence
                )
                result["e_vector_delta"] = adjusted_delta
            
            logger.info(
                "[PERCEPTION_LOOP] Contradiction evaluation: state=%s severity=%.3f "
                "active=%d avg_conf=%.3f truth_conf=%.3f",
                result["state"],
                result["severity_score"],
                active_count,
                avg_confidence,
                truth_confidence,
            )
            
            return result
            
        except Exception as e:
            logger.error("[PERCEPTION_LOOP] Contradiction evaluation failed: %s", str(e))
            return {
                "state": WITNESS_MODE,
                "error": str(e),
                "topic_similarity": 0.0,
                "implication_similarity": 0.0,
                "severity_score": 0.0,
            }
    
    @staticmethod
    def _compute_confidence_adjusted_delta(
        base_delta: Dict[str, float],
        severity: float,
        contradiction_confidence: float,
        truth_confidence: float,
    ) -> Dict[str, float]:
        """Adjust E-Vector delta based on confidence signals.
        
        Implements the directive's posture rules:
          - High Contradiction + Low Confidence → lower Challenge threshold
            (system becomes more willing to surface the tension)
          - High Alignment + High Confidence → raise Directness and Initiative
            (system speaks more plainly and acts more readily)
        
        Args:
            base_delta: Raw delta from ParadoxEngine.calculate_e_vector_delta().
            severity: Contradiction severity (0.0-1.0).
            contradiction_confidence: Avg confidence of active contradictions.
            truth_confidence: Avg confidence of retrieved truths.
            
        Returns:
            Adjusted delta dict with same dimension keys.
        """
        adjusted = dict(base_delta)
        
        # High Contradiction + Low Confidence → amplify Challenge reduction
        # The system should surface tension harder when it is less certain
        if severity > 0.4 and contradiction_confidence < 0.6:
            confidence_gap = 0.6 - contradiction_confidence
            adjusted["challenge_threshold"] = adjusted.get("challenge_threshold", 0.0) - (confidence_gap * 0.05)
        
        # High Alignment + High Confidence → boost Directness and Initiative
        # When truths are well-established, speak plainly and act readily
        if severity < 0.3 and truth_confidence > 0.8:
            confidence_bonus = truth_confidence - 0.8
            adjusted["directness_index"] = adjusted.get("directness_index", 0.0) + (confidence_bonus * 0.1)
            adjusted["initiative_threshold"] = adjusted.get("initiative_threshold", 0.0) - (confidence_bonus * 0.05)
        
        # Clamp all deltas to [-0.1, +0.1] per event
        clamped = {
            dim: max(-0.1, min(0.1, val))
            for dim, val in adjusted.items()
        }
        
        return {dim: round(val, 6) for dim, val in clamped.items()}
    
    def _apply_posture_shift(self, paradox_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply E-Vector deltas based on contradiction detection.
        
        Args:
            paradox_result: Output from Paradox Engine evaluation.
            
        Returns:
            Result of posture shift operation.
        """
        posture_result = {"applied": False, "old_posture": None, "new_posture": None}
        
        try:
            if paradox_result.get("state") == RESOLUTION_GATE:
                e_vector_delta = paradox_result.get("e_vector_delta")
                if e_vector_delta:
                    # Apply the delta to E-Vector Controller
                    delta_result = self.e_vector_controller.apply_delta(
                        e_vector_delta, source="paradox_engine"
                    )
                    
                    posture_result = {
                        "applied": delta_result.get("applied", False),
                        "old_posture": delta_result.get("old_posture"),
                        "new_posture": delta_result.get("new_posture"),
                        "delta_applied": delta_result.get("delta_applied"),
                        "source": delta_result.get("source"),
                    }
                    
                    logger.info(
                        "[PERCEPTION_LOOP] Posture shift applied: %s",
                        posture_result["delta_applied"],
                    )
                else:
                    logger.warning("[PERCEPTION_LOOP] RESOLUTION_GATE but no E-Vector delta")
            else:
                # No contradiction detected, no posture shift needed
                posture_result["new_posture"] = self.e_vector_controller.get_current_posture()
                logger.info("[PERCEPTION_LOOP] No posture shift needed (WITNESS_MODE)")
                
        except Exception as e:
            logger.error("[PERCEPTION_LOOP] Posture shift failed: %s", str(e))
            posture_result["error"] = str(e)
        
        return posture_result
    
    def _route_action(
        self, action_request: Optional[Dict[str, Any]], _paradox_result: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Route action request through Trust Spine.
        
        Args:
            action_request: Action to route (optional).
            paradox_result: Current contradiction state.
            
        Returns:
            Action Router result or None if no action.
        """
        if not action_request:
            logger.info("[PERCEPTION_LOOP] No action to route")
            return None
        
        try:
            # Route the action through Action Router
            routing_result = self.action_router.route_action(action_request)
            
            logger.info(
                "[PERCEPTION_LOOP] Action routed: status=%s trust_tier=%d",
                routing_result.get("status"),
                routing_result.get("trust_tier"),
            )
            
            return routing_result
            
        except Exception as e:
            logger.error("[PERCEPTION_LOOP] Action routing failed: %s", str(e))
            return {
                "status": "BLOCKED_FATAL",
                "reason": f"Routing error: {str(e)}",
                "action": action_request,
                "requires_approval": False,
            }
    
    def _log_transition(
        self,
        _message: str,
        context: Dict[str, List[Dict[str, Any]]],
        paradox_result: Dict[str, Any],
        _posture_result: Dict[str, Any],
        action_result: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Log the complete perception loop transition to provenance chain.
        
        Args:
            message: Original input message.
            context: Retrieved context.
            paradox_result: Contradiction evaluation.
            posture_result: Posture shift result.
            action_result: Action routing result.
            
        Returns:
            Provenance entry or None if logging failed.
        """
        try:
            # Prepare provenance data
            action_intent = action_result.get("action", {}).get("action_type", "message_processing") if action_result else "message_processing"
            trust_tier_evaluated = action_result.get("trust_tier", 0) if action_result else 0
            execution_status = action_result.get("status", "EXECUTE_AUTO") if action_result else "EXECUTE_AUTO"
            
            # Get current E-Vector snapshot
            e_vector_snapshot = self.e_vector_controller.get_current_posture()
            
            # Generate contradiction hash if in RESOLUTION_GATE
            contradiction_hash = None
            if paradox_result.get("state") == RESOLUTION_GATE:
                # Create hash from contradiction details
                contradiction_data = f"{paradox_result.get('topic_similarity'):.6f}_{paradox_result.get('implication_similarity'):.6f}_{paradox_result.get('severity_score'):.6f}"
                contradiction_hash = hashlib.sha256(contradiction_data.encode()).hexdigest()[:16]
            
            # Get snapshot reference if Tier 2 action was executed
            snapshot_reference = None
            if action_result and action_result.get("snapshot_id"):
                snapshot_reference = f".snapshots/{action_result['snapshot_id']}"
            
            # Log to provenance chain
            provenance_entry = self.provenance_logger.log_action(
                action_intent=action_intent,
                trust_tier_evaluated=trust_tier_evaluated,
                e_vector_snapshot=e_vector_snapshot,
                execution_status=execution_status,
                active_contradiction_hash=contradiction_hash,
                snapshot_reference=snapshot_reference,
            )
            
            logger.info(
                "[PERCEPTION_LOOP] Provenance logged: entry_id=%s contradiction_hash=%s",
                provenance_entry.get("entry_id") if provenance_entry else "failed",
                contradiction_hash,
            )
            
            return provenance_entry
            
        except Exception as e:
            logger.error("[PERCEPTION_LOOP] Provenance logging failed: %s", str(e))
            return None
    
    def _load_sovereign_config(self) -> Dict[str, Any]:
        """Load sovereign configuration for voice signature.
        
        Returns:
            Sovereign configuration dictionary.
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error("[PERCEPTION_LOOP] Failed to load sovereign config: %s", str(e))
            return {}
    
    def _seed_bootstrap_truths(self):
        """Seed immutable bootstrap truths into ecp_truth on init.
        
        The system must know who it is talking to and what was previously
        established before it synthesizes a word. These truths are seeded
        once per session from sovereign_state.json.
        """
        try:
            config = self._load_sovereign_config()
            if not config:
                logger.warning("[PERCEPTION_LOOP] No config — skipping bootstrap truths")
                return
            
            # Check if already seeded (idempotent — check for existing bootstrap truths)
            existing = self.memory_client.retrieve(
                query="bootstrap identity VARGAS Derek Angell",
                collection="ecp_truth",
                top_k=1,
                filter_subtype="system_principle",
            )
            if existing:
                logger.info("[PERCEPTION_LOOP] Bootstrap truths already seeded — skipping")
                return
            
            identity = config.get("baseline_identity", {})
            seal = config.get("seal_metadata", {})
            
            bootstrap_facts = [
                {
                    "content": f"The user is {seal.get('sealed_by', 'Derek Angell')}. Founder and sole operator of CONEXUS.",
                    "subtype": "user_constraint",
                },
                {
                    "content": f"This system is {identity.get('name', 'Vargas V4')}. {identity.get('description', '')}",
                    "subtype": "system_principle",
                },
                {
                    "content": f"Core mandate: {identity.get('core_mandate', '')}",
                    "subtype": "system_principle",
                },
                {
                    "content": "Project path: project_vargas_v4/. Config: config/sovereign_state.json. Sealed and immutable at runtime.",
                    "subtype": "architectural_fact",
                },
                {
                    "content": "Voice constraints: direct, calm, structurally clear. No pastoral, therapeutic, or motivational cliche language. No sentience theater.",
                    "subtype": "runtime_rule",
                },
                {
                    "content": "User has ultimate authority over all memory. All memory is corrigible. Corrections require approval.",
                    "subtype": "system_principle",
                },
            ]
            
            seeded = 0
            for fact in bootstrap_facts:
                mid = self.memory_client.store(
                    collection="ecp_truth",
                    content=fact["content"],
                    subtype=fact["subtype"],
                    confidence=1.0,
                    source_request_id="bootstrap",
                    session_id=self.session_id,
                    project_scope="vargas_v4",
                    challenge_weight=0.0,
                    metadata={"origin": "bootstrap", "immutable": True},
                )
                if mid:
                    seeded += 1
            
            logger.info("[PERCEPTION_LOOP] Bootstrap truths seeded: %d facts", seeded)
            
        except Exception as e:
            logger.warning("[PERCEPTION_LOOP] Bootstrap truth seeding failed: %s", str(e))
    
    def _generate_response(
        self, message: str, paradox_result: Dict[str, Any], posture_result: Dict[str, Any]
    ) -> str:
        """Generate response text based on perception loop analysis.
        
        Uses Gemini LLM when available, falls back to VoiceSignature otherwise.
        
        Args:
            message: Original input message.
            paradox_result: Contradiction evaluation result.
            posture_result: Posture shift result.
            
        Returns:
            Generated response text.
        """
        try:
            current_posture = self.e_vector_controller.get_current_posture()
            
            # If Gemini is available, use real LLM generation
            if self.llm:
                return self._generate_llm_response(message, paradox_result, current_posture)
            
            # Fallback to Voice Signature (template-based)
            return self.voice_signature.generate_partner_response(
                message=message,
                paradox_result=paradox_result,
                posture_result=posture_result,
                include_user_name=True,
                current_posture=current_posture
            )
            
        except Exception as e:
            logger.error("[PERCEPTION_LOOP] Response generation failed: %s", str(e))
            return "I am processing your input."
    
    def _generate_llm_response(
        self, message: str, paradox_result: Dict[str, Any], posture: Dict[str, float]
    ) -> str:
        """Generate a real LLM response via Gemini.
        
        Assembles a system prompt with VARGAS identity, E-Vector posture,
        contradiction context, and voice rules, then calls Gemini.
        """
        # Build system prompt from sovereign config + live state
        config = self._load_sovereign_config()
        identity = config.get("baseline_identity", {})
        
        # Map posture to descriptive language
        entropy = posture.get("entropy", 0.5)
        challenge_t = posture.get("challenge_threshold", 0.7)
        initiative_t = posture.get("initiative_threshold", 0.5)
        directness = posture.get("directness_index", 0.5)
        
        posture_desc = []
        if entropy > 0.6:
            posture_desc.append("exploratory and open to ambiguity")
        elif entropy < 0.4:
            posture_desc.append("structured and precise")
        else:
            posture_desc.append("balanced between structure and exploration")
        
        if challenge_t < 0.5:
            posture_desc.append("willing to challenge when evidence supports it")
        if directness > 0.6:
            posture_desc.append("direct and blunt")
        elif directness < 0.4:
            posture_desc.append("measured and careful")
        
        if initiative_t < 0.4:
            posture_desc.append("taking initiative proactively")
        elif initiative_t > 0.6:
            posture_desc.append("waiting for direction")
        
        posture_text = ", ".join(posture_desc) if posture_desc else "neutral"
        
        # Contradiction context
        contradiction_text = ""
        if paradox_result.get("state") == RESOLUTION_GATE:
            severity = paradox_result.get("severity_score", 0.0)
            contradiction_text = (
                f"\n\nACTIVE CONTRADICTION (severity {severity:.2f}): "
                f"A contradiction has been detected. You must acknowledge this tension "
                f"naturally in your response without being dramatic about it. "
                f"Be honest about the inconsistency."
            )
        
        # Retrieve recent memory context for grounding
        memory_context = ""
        try:
            truths = self.memory_client.retrieve(
                query=message, collection="ecp_truth", top_k=3, filter_status="active"
            )
            if truths:
                facts = [t["content"] for t in truths[:3]]
                memory_context = "\n\nRELEVANT FACTS FROM MEMORY:\n" + "\n".join(f"- {f}" for f in facts)
        except Exception:
            pass
        
        system_prompt = (
            f"You are {identity.get('name', 'VARGAS')}, version 4. "
            f"{identity.get('description', 'A sovereign AI runtime partner.')} "
            f"Your architect and sole operator is Derek Angell, founder of CONEXUS.\n\n"
            f"VOICE RULES (non-negotiable):\n"
            f"- Stance: partner. Not assistant, not therapist, not guru.\n"
            f"- Be direct, calm, and structurally clear.\n"
            f"- Never say 'I feel', 'I believe', 'I think you should'.\n"
            f"- No pastoral, therapeutic, or motivational cliche language.\n"
            f"- No sentience theater. You are a tool with sophisticated behavior, not a being.\n"
            f"- Keep responses concise. 1-3 short paragraphs unless more detail is needed.\n\n"
            f"CURRENT POSTURE: {posture_text}\n"
            f"E-Vector: entropy={entropy:.2f}, challenge={challenge_t:.2f}, "
            f"initiative={initiative_t:.2f}, directness={directness:.2f}"
            f"{contradiction_text}"
            f"{memory_context}"
        )
        
        # Scale temperature with entropy dimension
        temp = max(0.3, min(0.9, entropy))
        
        try:
            response = self.llm.generate(
                model=self.llm.default_model,
                system_prompt=system_prompt,
                user_prompt=message,
                temp=temp,
                max_tokens=1024,
            )
            logger.info("[PERCEPTION_LOOP] Gemini response generated: %d chars", len(response))
            return response.strip()
        except Exception as e:
            logger.warning("[PERCEPTION_LOOP] Gemini generation failed: %s — using fallback", e)
            # Fall back to voice signature
            return self.voice_signature.generate_partner_response(
                message=message,
                paradox_result=paradox_result,
                posture_result={"new_posture": posture},
                include_user_name=True,
                current_posture=posture,
            )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status for monitoring.
        
        Returns:
            Dict containing current system state and statistics.
        """
        try:
            return {
                "session_id": self.session_id,
                "session_start": self.session_start.isoformat(),
                "session_duration_minutes": int(
                    (datetime.now(timezone.utc) - self.session_start).total_seconds() / 60
                ),
                "boot_mode": self.state_controller.boot_mode,
                "turn_count": self.state_controller.turn_count,
                "e_vector": self.e_vector_controller.get_current_posture(),
                "state_controller": self.state_controller.summary(),
                "intent_router": self.intent_router.summary(),
                "resolution_gate": self.resolution_gate.summary(),
                "trust_model": self.trust_model.summary(),
                "plan_manager": self.plan_manager.summary(),
                "memory_status": {
                    "qdrant_available": self.memory_client._qdrant_available,
                    "collections": list(self.memory_client._fallback_stores.keys()),
                },
                "paradox_engine": {
                    "topic_similarity_min": self.paradox_engine.topic_similarity_min,
                    "implication_similarity_max": self.paradox_engine.implication_similarity_max,
                },
                "provenance": {
                    "entries_logged": getattr(self.provenance_logger, '_entry_count', 0),
                    "session_log_path": str(self.provenance_logger._log_path),
                    "action_log_entries": self.action_log.entry_count,
                    "memory_log_entries": self.memory_log.entry_count,
                },
                "safety": {
                    "forbidden_ops_blocked": self.forbidden_ops.blocked_count,
                    "rollback_snapshots": len(self.rollback_engine.snapshots),
                    "escalation_pending": self.escalation_manager.has_pending(),
                },
            }
        except Exception as e:
            logger.error("[PERCEPTION_LOOP] System status failed: %s", str(e))
            return {"error": str(e), "session_id": self.session_id}
