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
    current_gear: Literal["DIVERGE", "GATHER", "CONTRADICTION_DETECTION", "COLLAPSE", "EXECUTE", "REFLECT", "BECOME", "INTEGRATE", "RETURN"]
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

# Skill Permissions per Gear
GEAR_SKILL_PERMISSIONS = {
    "DIVERGE": ["hierarchical-planning", "paradox-processing"],
    "GATHER": ["memory-management", "autonomous-tool-use"],
    "CONTRADICTION_DETECTION": ["paradox-processing", "ethics-value-integration"],
    "COLLAPSE": ["mission-compression", "stress-navigation"],
    "EXECUTE": ["secure-execution", "autonomous-tool-use"],
    "REFLECT": ["memory-management", "protocol-driven-reasoning"],
    "BECOME": ["identity-expansion", "emotional-symbolic-modulation"],
    "INTEGRATE": ["memory-management", "self-evolving-loop"],
    "RETURN": ["protocol-driven-reasoning"]
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
    """Process paradoxes within the symbolic field"""
    # Simplified paradox detection
    paradoxes = []
    if state["mode"] == "collapse":
        paradoxes.append({
            "type": "efficiency_vs_creativity",
            "description": "Balancing optimization with innovation",
            "resolution": "prioritize_efficiency"
        })
    elif state["mode"] == "become":
        paradoxes.append({
            "type": "growth_vs_stability",
            "description": "Balancing expansion with coherence",
            "resolution": "prioritize_growth"
        })
    
    state["paradoxes"] = paradoxes
    state["reasoning_trace"].append({
        "step": "ecp_contradiction",
        "paradoxes": paradoxes,
        "timestamp": datetime.now()
    })
    return state

def ecp_mode_activation(state: ConexusState) -> ConexusState:
    """Activate Collapse or Become mode"""
    # Mode determination based on gear and context
    if state["current_gear"] in ["COLLAPSE", "EXECUTE"]:
        state["mode"] = "collapse"
    elif state["current_gear"] in ["BECOME", "INTEGRATE"]:
        state["mode"] = "become"
    else:
        # DIVERGE, GATHER, etc. - context-dependent
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

# Gear Node Functions
def node_diverge(state: ConexusState) -> ConexusState:
    """DIVERGE Gear - Expansive exploration"""
    state["current_gear"] = "DIVERGE"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    # Load allowed skills
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["DIVERGE"]
    state["active_agent"] = "sway"  # Sway leads exploration
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "DIVERGE",
        "next_gear": "GATHER",
        "timestamp": datetime.now()
    })
    return state

def node_gather(state: ConexusState) -> ConexusState:
    """GATHER Gear - Information collection"""
    state["current_gear"] = "GATHER"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["GATHER"]
    state["active_agent"] = "sway"
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "GATHER",
        "next_gear": "CONTRADICTION_DETECTION",
        "timestamp": datetime.now()
    })
    return state

def node_contradiction_detection(state: ConexusState) -> ConexusState:
    """CONTRADICTION_DETECTION Gear - Paradox identification"""
    state["current_gear"] = "CONTRADICTION_DETECTION"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["CONTRADICTION_DETECTION"]
    state["active_agent"] = "sway"
    
    # Determine next gear based on paradox detection
    next_gear = "COLLAPSE" if state["paradoxes"] else "EXECUTE"
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "CONTRADICTION_DETECTION",
        "next_gear": next_gear,
        "paradoxes_found": len(state["paradoxes"]),
        "timestamp": datetime.now()
    })
    return state

def node_collapse(state: ConexusState) -> ConexusState:
    """COLLAPSE Gear - Mission compression"""
    state["current_gear"] = "COLLAPSE"
    state["mode"] = "collapse"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["COLLAPSE"]
    state["active_agent"] = "sway"
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "COLLAPSE",
        "next_gear": "EXECUTE",
        "timestamp": datetime.now()
    })
    return state

def node_execute(state: ConexusState) -> ConexusState:
    """EXECUTE Gear - Decisive action"""
    state["current_gear"] = "EXECUTE"
    state["mode"] = "collapse"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["EXECUTE"]
    state["active_agent"] = "sway"
    
    # Check execution authorization
    state["execution_authorized"] = state["policy_compliance"]
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "EXECUTE",
        "next_gear": "REFLECT",
        "execution_authorized": state["execution_authorized"],
        "timestamp": datetime.now()
    })
    return state

def node_reflect(state: ConexusState) -> ConexusState:
    """REFLECT Gear - Post-execution reflection"""
    state["current_gear"] = "REFLECT"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["REFLECT"]
    state["active_agent"] = "opie"  # Opie leads reflection
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "REFLECT",
        "next_gear": "BECOME",
        "timestamp": datetime.now()
    })
    return state

def node_become(state: ConexusState) -> ConexusState:
    """BECOME Gear - Identity expansion"""
    state["current_gear"] = "BECOME"
    state["mode"] = "become"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["BECOME"]
    state["active_agent"] = "opie"
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "BECOME",
        "next_gear": "INTEGRATE",
        "timestamp": datetime.now()
    })
    return state

def node_integrate(state: ConexusState) -> ConexusState:
    """INTEGRATE Gear - Knowledge integration"""
    state["current_gear"] = "INTEGRATE"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["INTEGRATE"]
    state["active_agent"] = "opie"
    
    state["reasoning_trace"].append({
        "step": "gear_complete",
        "gear": "INTEGRATE",
        "next_gear": "RETURN",
        "timestamp": datetime.now()
    })
    return state

def node_return(state: ConexusState) -> ConexusState:
    """RETURN Gear - Cycle completion"""
    state["current_gear"] = "RETURN"
    state = ecp_truth(state)
    state = ecp_symbol(state)
    state = ecp_contradiction(state)
    state = ecp_mode_activation(state)
    state = ecp_polarity_emergence(state)
    
    state["skills_loaded"] = GEAR_SKILL_PERMISSIONS["RETURN"]
    state["active_agent"] = "opie"
    
    state["completion_status"] = "complete"
    state["reasoning_trace"].append({
        "step": "cycle_complete",
        "gear": "RETURN",
        "next_cycle": "DIVERGE",
        "timestamp": datetime.now()
    })
    return state

# Build the State Graph
def create_conexus_graph() -> StateGraph:
    """Create the CONEXUS Nine Gears state machine"""
    
    # Initialize the graph
    workflow = StateGraph(ConexusState)
    
    # Add nodes
    workflow.add_node("DIVERGE", node_diverge)
    workflow.add_node("GATHER", node_gather)
    workflow.add_node("CONTRADICTION_DETECTION", node_contradiction_detection)
    workflow.add_node("COLLAPSE", node_collapse)
    workflow.add_node("EXECUTE", node_execute)
    workflow.add_node("REFLECT", node_reflect)
    workflow.add_node("BECOME", node_become)
    workflow.add_node("INTEGRATE", node_integrate)
    workflow.add_node("RETURN", node_return)
    
    # Add edges (sequential flow)
    workflow.add_edge("DIVERGE", "GATHER")
    workflow.add_edge("GATHER", "CONTRADICTION_DETECTION")
    
    # Conditional edge from CONTRADICTION_DETECTION
    workflow.add_conditional_edges(
        "CONTRADICTION_DETECTION",
        lambda state: "COLLAPSE" if state["paradoxes"] else "EXECUTE",
        {
            "COLLAPSE": "COLLAPSE",
            "EXECUTE": "EXECUTE"
        }
    )
    
    workflow.add_edge("COLLAPSE", "EXECUTE")
    workflow.add_edge("EXECUTE", "REFLECT")
    workflow.add_edge("REFLECT", "BECOME")
    workflow.add_edge("BECOME", "INTEGRATE")
    workflow.add_edge("INTEGRATE", "RETURN")
    workflow.add_edge("RETURN", END)
    
    # Set entry point
    workflow.set_entry_point("DIVERGE")
    
    # Add memory for persistence
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)

# Initialize state function
def initialize_state(task_input: str) -> ConexusState:
    """Initialize CONEXUS state for a new task"""
    return {
        "current_gear": "DIVERGE",
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
