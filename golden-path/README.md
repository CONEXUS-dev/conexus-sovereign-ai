# CONEXUS Golden Path Implementation

## Overview
This directory contains the complete golden path implementation for the CONEXUS sovereign system, validating the entire technology stack with Qdrant memory substrate and LangGraph orchestration backbone.

## Architecture

### Components
- **Qdrant**: Vector database for memory management (episodic, semantic, sovereign, lineage namespaces)
- **LangGraph**: State machine orchestration for Nine Gears + ECP protocol
- **Skills Integration**: All 14 CONEXUS skills with proper permissions
- **Security Layer**: Policy enforcement and audit logging
- **Test Runner**: Complete validation suite

### Memory Namespaces
- **episodic**: Lived experience, runs, outcomes
- **semantic**: Learned truths, stable knowledge  
- **sovereign**: Identity, values, protocols
- **lineage**: Evolution history, confidence, provenance

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Sufficient memory for vector operations

### Deployment
```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# Run golden path test
docker-compose --profile test run test-runner
```

### Manual Testing
```bash
# Check Qdrant health
curl http://localhost:6333/health

# Check LangGraph health  
curl http://localhost:8000/health

# Run test manually
python test-runner.py
```

## File Structure
```
golden-path/
├── README.md                    # This file
├── docker-compose.yml          # Service orchestration
├── qdrant-config.yaml          # Vector database configuration
├── langgraph-state-machine.py  # Nine Gears + ECP implementation
├── test-runner.py              # Validation suite
├── golden-path-run-spec.md     # Complete specification
└── test-results/               # Test output directory
```

## Success Criteria

### Protocol Compliance
- [ ] All Nine Gears executed in sequence
- [ ] ECP micro-sequence completed at each gear
- [ ] Mode transitions followed protocol rules
- [ ] State transitions explicit and logged

### Memory Integration  
- [ ] All collections created with proper schema
- [ ] Memory writes through Memory Management skill only
- [ ] Provenance tracking complete on all writes
- [ ] Retrieval operations successful

### Security Enforcement
- [ ] Secure Execution validated all actions
- [ ] Policy compliance checked at each step
- [ ] Audit trail complete and immutable
- [ ] No unauthorized skill access

### Performance Metrics
- Total execution time: < 5 minutes
- Memory operations: > 10 successful writes
- Skill invocations: 14 skills executed
- Security checks: 100% pass rate
- Reasoning trace: > 50 steps
- Confidence score: > 0.8

## Validation Results

After successful completion, the system demonstrates:
- Complete protocol execution without errors
- Memory integration with provenance tracking
- Security enforcement throughout
- Skill integration with proper permissions
- Complete reasoning trace and explainability
- System resilience under stress

## Next Steps

After golden path validation:
1. Scale to multi-agent deployment
2. Enable autonomous evolution features
3. Implement advanced monitoring
4. Deploy to production environment

## Troubleshooting

### Common Issues
- **Qdrant connection failed**: Check container health and network
- **LangGraph timeout**: Increase timeout or check resource allocation
- **Skill loading errors**: Verify skill paths and permissions
- **Memory write failures**: Check Qdrant collection schemas

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python test-runner.py --verbose
```

## Architecture Notes

### Sovereignty Preservation
- Qdrant stores memory without interpretation
- LangGraph enforces protocol without invention
- Skills maintain authority and permissions
- Security layer provides non-negotiable boundaries

### Protocol Implementation
- Nine Gears as explicit state machine nodes
- ECP micro-sequence as sub-graph
- Conditional routing based on paradox detection
- Mode-specific skill loading and execution

### Memory Governance
- All writes through Memory Management skill
- Provenance tracking on all operations
- Namespace separation for different memory types
- Audit logging for complete traceability

This implementation validates that CONEXUS can operate as a truly sovereign, governed, and resilient system.
