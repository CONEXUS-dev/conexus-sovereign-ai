"""
CONEXUS LangGraph State Machine Implementation
Nine Gears Macro-Sequence with ECP Micro-Sequence
"""

from typing import TypedDict, Literal, Dict, List, Any
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

class ConexusState(TypedDict):
    # Protocol State
    current_gear: Literal["INNOVATION_RAPPORT", "STRATEGIC_TRUTH", "CREATIVE_SYMBOL", "BUSINESS_ART_CONTRADICTION", "VISION_HOLD", "MARKET_ROAM", "PERFORMANCE_STRESS", "ETHICS_VALUE", "SUCCESS_CONTINUITY_SEAL"]
    mode: Literal["collapse", "become"]
    
    # ECP State
    truth: str
    symbolic_packet: Dict[str, Any]
    paradoxes: List[Dict[str, Any]]
    
    # Agent State
    active_agent: Literal["sway", "opie"]
    skills_loaded: List[str]
    
    # Memory State
    episodic_context: List[Dict[str, Any]]
    semantic_context: List[Dict[str, Any]]
    
    # Security State
    execution_authorized: bool
    policy_compliance: bool
    
    # Audit State
    reasoning_trace: List[Dict[str, Any]]
    confidence_score: float
    timestamp: datetime
    
    # Task State
    task_input: str
    task_output: str
    completion_status: str

# Skill Permissions per Gear (v1.1 Nine Gears Unified)
GEAR_SKILL_PERMISSIONS = {
    "INNOVATION_RAPPORT": ["paradox-processing", "emotional-symbolic-modulation"],
    "STRATEGIC_TRUTH": ["hierarchical-planning", "protocol-driven-reasoning"],
    "CREATIVE_SYMBOL": ["emotional-symbolic-modulation", "identity-expansion"],
    "BUSINESS_ART_CONTRADICTION": ["paradox-processing", "ethics-value-integration"],
    "VISION_HOLD": ["mission-compression", "identity-expansion"],
    "MARKET_ROAM": ["autonomous-tool-use", "memory-management"],
    "PERFORMANCE_STRESS": ["stress-navigation", "secure-execution"],
    "ETHICS_VALUE": ["ethics-value-integration", "protocol-driven-reasoning"],
    "SUCCESS_CONTINUITY_SEAL": ["memory-management", "self-evolving-loop"]
}

# ECP Micro-Sequence Functions
def ecp_truth(state: ConexusState) -> ConexusState:
    """State the current gear (Truth)"""
    state["truth"] = f"Current gear: {state['current_gear']}"
    state["reasoning_trace"].append({
        "step": "ecp_truth",
        "gear": state["current_gear"],
        "output": state["truth"],
        "timestamp": datetime.now()
    })
    return state

def ecp_symbol(state: ConexusState) -> ConexusState:
    """Hold the full symbolic packet"""
    state["symbolic_packet"] = {
        "gear": state["current_gear"],
        "mode": state["mode"],
        "context": {
            "episodic": state["episodic_context"],
            "semantic": state["semantic_context"],
            "task": state["task_input"]
        },
        "emotional_field": {
            "stress_level": "moderate",  # Would come from Stress Navigation
            "confidence": state["confidence_score"],
            "coherence": "high"
        }
    }
    state["reasoning_trace"].append({
        "step": "ecp_symbol",
        "symbolic_packet": state["symbolic_packet"],
        "timestamp": datetime.now()
    })
    return state

def ecp_contradiction(state: ConexusState) -> ConexusState:
    """Explicitly hold paradoxes — Patent-7-correct implementation.
    
    Collapse Mode: resolve contradiction into a single directive.
    Become Mode: integrate contradiction without resolution.
    Symbolic field remains implicit as contextual bias.
    """
    paradoxes = [
        {"pole_a": "structured efficiency", "pole_b": "chaotic breakthrough", "status": "held"},
        {"pole_a": "profit", "pole_b": "purpose", "status": "held"},
        {"pole_a": "tradition", "pole_b": "innovation", "status": "held"},
        {"pole_a": "process", "pole_b": "inspiration", "status": "held"},
        {"pole_a": "quarterly pressure", "pole_b": "radical vision", "status": "held"},
    ]
    
    if state["mode"] == "collapse":
        for p in paradoxes:
            p["status"] = "resolved_to_directive"
    
    state["paradoxes"] = paradoxes
    state["reasoning_trace"].append({
        "step": "ecp_contradiction",
        "paradoxes": paradoxes,
        "mode": state["mode"],
        "timestamp": datetime.now()
    })
    return state

def ecp_mode_activation(state: ConexusState) -> ConexusState:
    """Activate Collapse or Become mode based on gear context"""
    # Mode determination based on v1.1 Nine Gears
    collapse_gears = ["STRATEGIC_TRUTH", "VISION_HOLD", "PERFORMANCE_STRESS", "SUCCESS_CONTINUITY_SEAL"]
    become_gears = ["INNOVATION_RAPPORT", "CREATIVE_SYMBOL", "ETHICS_VALUE"]
    
    if state["current_gear"] in collapse_gears:
        state["mode"] = "collapse"
    elif state["current_gear"] in become_gears:
        state["mode"] = "become"
    else:
        # BUSINESS_ART_CONTRADICTION, MARKET_ROAM - context-dependent
        state["mode"] = "collapse" if state["confidence_score"] > 0.7 else "become"
    
    state["reasoning_trace"].append({
        "step": "ecp_mode_activation",
        "mode": state["mode"],
        "timestamp": datetime.now()
    })
    return state

def ecp_polarity_emergence(state: ConexusState) -> ConexusState:
    """Allow polarity between optimization and creation to emerge"""
    polarity_output = {
        "mode": state["mode"],
        "gear": state["current_gear"],
        "emergent_quality": "decisive" if state["mode"] == "collapse" else "creative",
        "symbolic_resonance": "compressed" if state["mode"] == "collapse" else "expanded"
    }
    
    state["reasoning_trace"].append({
        "step": "ecp_polarity_emergence",
        "output": polarity_output,
        "timestamp": datetime.now()
    })
    return state

# Gear Node Functions (v1.1 Nine Gears Unified)
def node_innovation_rapport(state: ConexusState) -> ConexusState:
    """Gear 1: Innovation Rapport — Establish presence within the contradiction field"""
    state["current_gear"] = "INNOVATION_RAPPORT"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["INNOVATION_RAPPORT"]
    state["active_agent"] = "opie"  # Become-leaning gear
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "INNOVATION_RAPPORT",
        "next_gear": "STRATEGIC_TRUTH",
        "timestamp": datetime.now()
    })
    return state

def node_strategic_truth(state: ConexusState) -> ConexusState:
    """Gear 2: Strategic Truth — Name the core reality without abstraction"""
    state["current_gear"] = "STRATEGIC_TRUTH"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["STRATEGIC_TRUTH"]
    state["active_agent"] = "sway"  # Collapse-leaning gear
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "STRATEGIC_TRUTH",
        "next_gear": "CREATIVE_SYMBOL",
        "timestamp": datetime.now()
    })
    return state

def node_creative_symbol(state: ConexusState) -> ConexusState:
    """Gear 3: Creative Symbol — Activate symbolic bias through tone and posture"""
    state["current_gear"] = "CREATIVE_SYMBOL"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["CREATIVE_SYMBOL"]
    state["active_agent"] = "opie"  # Become-leaning gear
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "CREATIVE_SYMBOL",
        "next_gear": "BUSINESS_ART_CONTRADICTION",
        "timestamp": datetime.now()
    })
    return state

def node_business_art_contradiction(state: ConexusState) -> ConexusState:
    """Gear 4: Business-Art Contradiction — Hold or resolve tension depending on mode"""
    state["current_gear"] = "BUSINESS_ART_CONTRADICTION"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["BUSINESS_ART_CONTRADICTION"]
    state["active_agent"] = "sway" if state["mode"] == "collapse" else "opie"
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "BUSINESS_ART_CONTRADICTION",
        "next_gear": "VISION_HOLD",
        "paradoxes_held": len(state["paradoxes"]),
        "timestamp": datetime.now()
    })
    return state

def node_vision_hold(state: ConexusState) -> ConexusState:
    """Gear 5: Vision Hold — Collapse: compress vision; Become: expand vision"""
    state["current_gear"] = "VISION_HOLD"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["VISION_HOLD"]
    state["active_agent"] = "sway"  # Collapse-leaning gear
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "VISION_HOLD",
        "next_gear": "MARKET_ROAM",
        "timestamp": datetime.now()
    })
    return state

def node_market_roam(state: ConexusState) -> ConexusState:
    """Gear 6: Market Roam — Explore or target the landscape explicitly"""
    state["current_gear"] = "MARKET_ROAM"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["MARKET_ROAM"]
    state["active_agent"] = "sway" if state["mode"] == "collapse" else "opie"
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "MARKET_ROAM",
        "next_gear": "PERFORMANCE_STRESS",
        "timestamp": datetime.now()
    })
    return state

def node_performance_stress(state: ConexusState) -> ConexusState:
    """Gear 7: Performance Stress — Navigate pressure without loss of coherence"""
    state["current_gear"] = "PERFORMANCE_STRESS"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["PERFORMANCE_STRESS"]
    state["active_agent"] = "sway"  # Collapse-leaning gear
    
    # Check execution authorization under stress
    state["execution_authorized"] = state["policy_compliance"]
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "PERFORMANCE_STRESS",
        "next_gear": "ETHICS_VALUE",
        "execution_authorized": state["execution_authorized"],
        "timestamp": datetime.now()
    })
    return state

def node_ethics_value(state: ConexusState) -> ConexusState:
    """Gear 8: Ethics / Value — Integrate moral, cultural, and symbolic frames"""
    state["current_gear"] = "ETHICS_VALUE"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["ETHICS_VALUE"]
    state["active_agent"] = "opie"  # Become-leaning gear
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "ETHICS_VALUE",
        "next_gear": "SUCCESS_CONTINUITY_SEAL",
        "timestamp": datetime.now()
    })
    return state

def node_success_continuity_seal(state: ConexusState) -> ConexusState:
    """Gear 9: Success Continuity Seal — Collapse: finalize; Become: integrate transformation"""
    state["current_gear"] = "SUCCESS_CONTINUITY_SEAL"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["SUCCESS_CONTINUITY_SEAL"]
    state["active_agent"] = "sway" if state["mode"] == "collapse" else "opie"
    
    state["completion_status"] = "complete"
    state["reasoning_trace"].append({
        "step": "cycle_complete",
        "gear": "SUCCESS_CONTINUITY_SEAL",
        "next_cycle": "INNOVATION_RAPPORT",
        "timestamp": datetime.now()
    })
    return state

# Build the State Graph
def create_conexus_graph() -> StateGraph:
    """Create the CONEXUS Nine Gears state machine (v1.1 Unified)"""
    
    # Initialize the graph
    workflow = StateGraph(ConexusState)
    
    # Add nodes (v1.1 Nine Gears)
    workflow.add_node("INNOVATION_RAPPORT", node_innovation_rapport)
    workflow.add_node("STRATEGIC_TRUTH", node_strategic_truth)
    workflow.add_node("CREATIVE_SYMBOL", node_creative_symbol)
    workflow.add_node("BUSINESS_ART_CONTRADICTION", node_business_art_contradiction)
    workflow.add_node("VISION_HOLD", node_vision_hold)
    workflow.add_node("MARKET_ROAM", node_market_roam)
    workflow.add_node("PERFORMANCE_STRESS", node_performance_stress)
    workflow.add_node("ETHICS_VALUE", node_ethics_value)
    workflow.add_node("SUCCESS_CONTINUITY_SEAL", node_success_continuity_seal)
    
    # Add edges (sequential flow through all 9 gears)
    workflow.add_edge("INNOVATION_RAPPORT", "STRATEGIC_TRUTH")
    workflow.add_edge("STRATEGIC_TRUTH", "CREATIVE_SYMBOL")
    workflow.add_edge("CREATIVE_SYMBOL", "BUSINESS_ART_CONTRADICTION")
    workflow.add_edge("BUSINESS_ART_CONTRADICTION", "VISION_HOLD")
    workflow.add_edge("VISION_HOLD", "MARKET_ROAM")
    workflow.add_edge("MARKET_ROAM", "PERFORMANCE_STRESS")
    workflow.add_edge("PERFORMANCE_STRESS", "ETHICS_VALUE")
    workflow.add_edge("ETHICS_VALUE", "SUCCESS_CONTINUITY_SEAL")
    workflow.add_edge("SUCCESS_CONTINUITY_SEAL", END)
    
    # Set entry point
    workflow.set_entry_point("INNOVATION_RAPPORT")
    
    # Add memory for persistence
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)

# Initialize state function
def initialize_state(task_input: str) -> ConexusState:
    """Initialize CONEXUS state for a new task"""
    return {
        "current_gear": "INNOVATION_RAPPORT",
        "mode": "collapse",
        "truth": "",
        "symbolic_packet": {},
        "paradoxes": [],
        "active_agent": "sway",
        "skills_loaded": [],
        "episodic_context": [],
        "semantic_context": [],
        "execution_authorized": False,
        "policy_compliance": True,
        "reasoning_trace": [],
        "confidence_score": 0.8,
        "timestamp": datetime.now(),
        "task_input": task_input,
        "task_output": "",
        "completion_status": "in_progress"
    }

if __name__ == "__main__":
    # Example usage
    graph = create_conexus_graph()
    initial_state = initialize_state("Analyze strategic tension between innovation and growth")
    
    # Run the graph
    result = graph.invoke(initial_state)
    
    print("CONEXUS Cycle Complete!")
    print(f"Final State: {result['completion_status']}")
    print(f"Reasoning Steps: {len(result['reasoning_trace'])}")
    print(f"Confidence Score: {result['confidence_score']}")
