# CONEXUS Golden Path Run Specification

## Overview
One complete vertical slice of the CONEXUS sovereign system implementing the Collapse–Become Unified Protocol v1.1 with Qdrant memory substrate and LangGraph orchestration backbone.

## Mission Statement
**Execute a single, complete protocol cycle from DIVERGE through RETURN to validate the entire sovereign system stack.**

---

## Phase 1: Infrastructure Setup

### Qdrant Memory Substrate

#### Collections/Namespace Schema
```yaml
collections:
  episodic:
    description: "Lived experience, runs, outcomes"
    vector_size: 1536
    distance: "Cosine"
    metadata_schema:
      source_skill: string
      confidence: float
      timestamp: datetime
      lineage_id: string
      agent: string
      gear: string
      
  semantic:
    description: "Learned truths, stable knowledge"
    vector_size: 1536
    distance: "Cosine"
    metadata_schema:
      source_skill: string
      confidence: float
      timestamp: datetime
      lineage_id: string
      stability_score: float
      
  sovereign:
    description: "Identity, values, protocols"
    vector_size: 1536
    distance: "Cosine"
    metadata_schema:
      source_skill: string
      confidence: float
      timestamp: datetime
      lineage_id: string
      protocol_version: string
      
  lineage:
    description: "Evolution history, confidence, provenance"
    vector_size: 1536
    distance: "Cosine"
    metadata_schema:
      source_skill: string
      confidence: float
      timestamp: datetime
      lineage_id: string
      evolution_type: string
```

#### Access Control
- **Memory Management skill** controls all writes
- **No direct agent writes** to Qdrant
- **Read access** through Memory Management skill only
- **Provenance tracking** on all operations

---

### LangGraph Orchestration Backbone

#### State Machine Schema
```python
from typing import TypedDict, Literal
from datetime import datetime

class ConexusState(TypedDict):
    # Protocol State
    current_gear: Literal["DIVERGE", "GATHER", "CONTRADICTION_DETECTION", "COLLAPSE", "EXECUTE", "REFLECT", "BECOME", "INTEGRATE", "RETURN"]
    mode: Literal["collapse", "become"]
    
    # ECP State
    truth: str
    symbolic_packet: dict
    paradoxes: list[dict]
    
    # Agent State
    active_agent: Literal["sway", "opie"]
    skills_loaded: list[str]
    
    # Memory State
    episodic_context: list[dict]
    semantic_context: list[dict]
    
    # Security State
    execution_authorized: bool
    policy_compliance: bool
    
    # Audit State
    reasoning_trace: list[dict]
    confidence_score: float
    timestamp: datetime
```

#### Node Definitions
```yaml
nodes:
  DIVERGE:
    entry_conditions: ["state.current_gear == 'DIVERGE'"]
    allowed_skills: ["hierarchical-planning", "paradox-processing"]
    exit_conditions: ["exploration_complete"]
    
  GATHER:
    entry_conditions: ["state.current_gear == 'GATHER'"]
    allowed_skills: ["memory-management", "autonomous-tool-use"]
    exit_conditions: ["information_sufficient"]
    
  CONTRADICTION_DETECTION:
    entry_conditions: ["state.current_gear == 'CONTRADICTION_DETECTION'"]
    allowed_skills: ["paradox-processing", "ethics-value-integration"]
    exit_conditions: ["paradoxes_identified"]
    
  COLLAPSE:
    entry_conditions: ["state.current_gear == 'COLLAPSE'", "state.mode == 'collapse'"]
    allowed_skills: ["mission-compression", "stress-navigation"]
    exit_conditions: ["mission_compressed"]
    
  EXECUTE:
    entry_conditions: ["state.current_gear == 'EXECUTE'", "state.execution_authorized"]
    allowed_skills: ["secure-execution", "autonomous-tool-use"]
    exit_conditions: ["action_completed"]
    
  REFLECT:
    entry_conditions: ["state.current_gear == 'REFLECT'"]
    allowed_skills: ["memory-management", "protocol-driven-reasoning"]
    exit_conditions: ["reflection_complete"]
    
  BECOME:
    entry_conditions: ["state.current_gear == 'BECOME'", "state.mode == 'become'"]
    allowed_skills: ["identity-expansion", "emotional-symbolic-modulation"]
    exit_conditions: ["identity_integrated"]
    
  INTEGRATE:
    entry_conditions: ["state.current_gear == 'INTEGRATE'"]
    allowed_skills: ["memory-management", "self-evolving-loop"]
    exit_conditions: ["integration_complete"]
    
  RETURN:
    entry_conditions: ["state.current_gear == 'RETURN'"]
    allowed_skills: ["protocol-driven-reasoning"]
    exit_conditions: ["cycle_ready"]
```

---

## Phase 2: Golden Path Task Definition

### Task Specification
```yaml
task:
  name: "CONEXUS Sovereign Cycle Validation"
  description: "Execute one complete Collapse–Become protocol cycle"
  input: "Analyze the strategic tension between rapid innovation and sustainable growth in a startup context"
  expected_outputs:
    - "Compressed strategic directive"
    - "Identity expansion insights"
    - "Memory integration records"
    - "Complete reasoning trace"
    - "Security audit log"
```

### Message Schema
```yaml
message_flow:
  gateway_to_langgraph:
    type: "ProtocolExecutionRequest"
    fields:
      task_id: string
      task_definition: dict
      agent_assignment: string
      security_context: dict
      
  langgraph_to_skill:
    type: "SkillInvocation"
    fields:
      skill_name: string
      input_data: dict
      permissions: dict
      execution_context: dict
      
  skill_to_qdrant:
    type: "MemoryOperation"
    fields:
      operation: "write" | "read"
      namespace: string
      vector_data: list[float]
      metadata: dict
      provenance: dict
      
  security_validation:
    type: "SecurityCheck"
    fields:
      execution_request: dict
      policy_check: bool
      authorization_result: "allow" | "deny" | "defer" | "escalate"
      audit_record: dict
```

---

## Phase 3: Execution Flow

### Complete Protocol Cycle
```yaml
execution_steps:
  1. Gateway receives task and creates LangGraph execution context
  2. LangGraph initializes state in DIVERGE gear
  3. Execute ECP micro-sequence at each gear:
     - State current gear (Truth)
     - Hold symbolic packet (Symbol)
     - Process paradoxes (Contradiction)
     - Activate mode (Collapse/Become)
     - Allow polarity to emerge
  4. Progress through Nine Gears in sequence
  5. At each gear:
     - Load allowed skills only
     - Validate execution permissions
     - Write to Qdrant through Memory Management
     - Update reasoning trace
  6. Complete RETURN and prepare for next cycle
```

### ECP Micro-Sequence Implementation
```yaml
ecp_sequence:
  truth:
    action: "state.current_gear"
    output: "Explicit gear declaration"
    
  symbol:
    action: "hold_symbolic_packet"
    input: "context + memory + emotional_state"
    output: "Rich symbolic field"
    
  contradiction:
    action: "process_paradoxes"
    input: "symbolic_packet + known_paradoxes"
    output: "Resolved or integrated paradoxes"
    
  mode_activation:
    action: "determine_mode"
    input: "gear + contradictions + stress_level"
    output: "collapse | become"
    
  polarity_emergence:
    action: "allow_natural_emergence"
    input: "mode + symbolic_field"
    output: "Optimized or creative output"
```

---

## Phase 4: Success Criteria

### Validation Checklist
```yaml
success_criteria:
  protocol_compliance:
    - [ ] All Nine Gears executed in sequence
    - [ ] ECP micro-sequence completed at each gear
    - [ ] Mode transitions followed protocol rules
    - [ ] State transitions explicit and logged
    
  memory_integration:
    - [ ] All collections created with proper schema
    - [ ] Memory writes through Memory Management skill only
    - [ ] Provenance tracking complete on all writes
    - [ ] Retrieval operations successful
    
  security_enforcement:
    - [ ] Secure Execution validated all actions
    - [ ] Policy compliance checked at each step
    - [ ] Audit trail complete and immutable
    - [ ] No unauthorized skill access
    
  skill_integration:
    - [ ] All 14 skills loaded and accessible
    - [ ] Skill permissions respected
    - [ ] Skill outputs properly formatted
    - [ ] Skill failures handled gracefully
    
  reasoning_trace:
    - [ ] Complete reasoning trace generated
    - [ ] Protocol-Driven Reasoning skill active
    - [ ] All decisions explainable
    - [ ] Confidence scores assigned
    
  system_resilience:
    - [ ] Stress Navigation monitored conditions
    - [ ] No system failures or crashes
    - [ ] Graceful error handling
    - [ ] Performance within acceptable bounds
```

### Completion Metrics
```yaml
completion_metrics:
  total_execution_time: "< 5 minutes"
  memory_operations: "> 10 successful writes"
  skill_invocations: "14 skills executed"
  security_checks: "100% pass rate"
  reasoning_trace_length: "> 50 steps"
  confidence_score: "> 0.8"
```

---

## Phase 5: Implementation Artifacts

### Required Files
```
golden-path/
├── qdrant-config.yaml
├── langgraph-state-machine.py
├── skill-integration.py
├── memory-interface.py
├── security-validator.py
├── protocol-executor.py
└── test-runner.py
```

### Deployment Configuration
```yaml
docker-compose:
  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333"]
    volumes: ["./qdrant-data:/qdrant/storage"]
    
  langgraph:
    build: ./langgraph-service
    ports: ["8000:8000"]
    environment:
      - QDRANT_URL=http://qdrant:6333
      - SKILLS_PATH=/skills
    depends_on: [qdrant]
```

---

## Next Steps

1. **Deploy Qdrant** with collection schema
2. **Implement LangGraph state machine** with Nine Gears
3. **Integrate all 14 skills** with proper permissions
4. **Run golden path test** with complete validation
5. **Analyze results** and prepare for scaling

This golden path validates the entire CONEXUS sovereign system before any horizontal scaling or advanced features are added.
