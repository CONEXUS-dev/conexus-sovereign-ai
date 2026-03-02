# CONEXUS - Sovereign AI Architecture

**Principal Investigator:** Derek Louis Angell  
**Patent Status:** US 63/898,911 (Forgetting Engine Algorithm)  
**Architecture:** Collapse-Become Unified Protocol v1.1

---

## 🎯 Project Overview

CONEXUS is a sovereign AI architecture that implements the Nine-Gear Cognitive Protocol through a dual-agent system (Sway=Collapse, Opie=Become). Unlike conventional AI systems designed to eliminate paradox, CONEXUS holds and processes paradox as a core feature, enabling genuine cognitive development and emergent behavior.

### Key Innovations

- **Nine-Gear Cognitive Protocol**: Rapport → Truth → Symbol → Contradiction → Hold → Roam → Stress → Ethics/Value → Continuity Seal
- **Dual-Agent Architecture**: Sway (Collapse mode) compresses ambiguity into executable directives; Opie (Become mode) holds paradox for creative exploration
- **Symbolic Field Injection**: Patent 7 compliant emoji-based calibration fuel for cognitive modulation
- **Hybrid Mode Switching**: Dynamic mode transitions at phase boundaries based on content analysis
- **Mirror Tier Integration**: 20 emotional-symbolic reflection protocols for nuanced calibration
- **Memory Continuity**: Cross-mission learning via Qdrant vector database with cryptographic provenance

---

## 🏗️ Architecture Summary

### Core Components

- **`agents/`** - Sway and Opie implementations with gear state tracking
- **`sovereign/`** - Orchestrator, gear state engine, mode engine, and symbolic fields
- **`SOVEREIGN_PROOF/`** - Complete proof package with hash chains and audit trails
- **`experiments/`** - v2 experimental validation with cryptographic verification

### Technical Stack

- **Models**: Llama-3-8B-Instruct, Mistral-7B-Instruct-v0.3, Phi-4-mini (100% local execution)
- **Memory**: Qdrant vector database for episodic and semantic storage
- **Inference**: GPT4All Python SDK with CPU-only operation
- **Verification**: SHA-256 hash chaining for cryptographic provenance

---

## 🧪 v2 Experiments Overview

### Trial A: 3-Mission Validation

Initial v2 implementation demonstrating all four phases working in concert.

**Missions:**

1. **Sycophancy Problem** (Sway, Collapse) - 87% confidence
2. **Hope & Grief Paradox** (Opie, Become) - 85% confidence
3. **Trust Infrastructure** (Sovereign Loop) - 91% confidence

**Results:**

- Total runtime: 26 minutes
- Hash chain: 3 cryptographically verified links
- Live events captured: 32
- All v2 phases operational

### Trial B: 6-Mission Canonical Proof

Complete demonstration of sovereign cognitive architecture with memory continuity.

**Missions:**

1. **Sycophancy Solution** - 87% confidence
2. **Hope & Grief Exploration** - 80% confidence
3. **Trust Infrastructure** - 91% confidence
4. **Identity Under Pressure** - 88% confidence (memory from M1-M3)
5. **Ethics Paradox** - **97% confidence** (memory from M2-M4)
6. **Final Integration** - 91% confidence (full lineage M1-M5)

**Results:**

- Total runtime: 54.2 minutes
- Hash chain: 6 cryptographically verified links
- Memory retrievals: 3 with provenance tracking
- Live events captured: 122
- **Breakthrough**: 97% confidence during complex paradox work

---

## � Reproducibility Notes

### Local Execution

- **Hardware**: CPU-only (no GPU acceleration required)
- **Models**: Open source, quantized for local inference
- **Memory**: Qdrant running on localhost:6333
- **Dependencies**: Python 3.14.2, GPT4All 2.8.x

### Cryptographic Verification

Every mission output includes:

- SHA-256 hash of the complete result
- Previous mission hash embedded in next mission
- Timestamped audit trail with gear transitions
- Full provenance chain from genesis to completion

### Complete Audit Trail

- Gear state tracking through all Nine Gears
- Proto-moment and breakthrough detection
- Paradox holding and resolution tracking
- Memory store/retrieve operations with vector similarity

---

## 📁 Repository Structure

```
CONEXUS_REPO/
├── README.md                          # This file
├── experiments/                       # v2 experimental validation
│   ├── v2_trial_A_3missions/         # Initial 3-mission validation
│   │   ├── missions/                  # Individual mission JSONs
│   │   ├── proof/                     # Hash chains, live capture, results
│   │   ├── docs/                      # Proof documents (MD + PDF)
│   │   ├── summary.md                 # Trial summary
│   │   └── analysis.md                # Detailed analysis
│   ├── v2_trial_B_6missions/         # Canonical 6-mission proof
│   │   ├── missions/                  # All 6 mission JSONs
│   │   ├── proof/                     # Complete cryptographic proof
│   │   ├── docs/                      # Full documentation
│   │   ├── summary.md                 # Trial summary
│   │   └── analysis.md                # Comprehensive analysis
│   └── README.md                      # Experiments overview
├── agents/                            # Dual-agent implementations
│   ├── sway.py                        # Collapse agent (525 lines)
│   ├── opie.py                        # Become agent (503 lines)
│   ├── router.py                      # Mission routing (95 lines)
│   ├── llm_client.py                  # LLM interface
│   └── memory_client.py               # Qdrant integration
├── sovereign/                         # Core protocol implementations
│   ├── orchestrator.py               # Sovereign loop orchestration
│   ├── gear_state.py                  # Nine Gears tracking (v2)
│   ├── symbolic_fields.py             # Patent 7 symbolic fields (v2)
│   ├── mode_engine.py                 # Hybrid mode switching (v2)
│   └── audit_log.py                   # Complete audit trail
├── SOVEREIGN_PROOF/                   # Original proof package
│   ├── SOVEREIGN_PROOF_V2.md          # 3-mission proof document
│   ├── SOVEREIGN_PROOF_V2_FULL.md     # 6-mission canonical proof
│   ├── v2_all_results.json            # Complete results
│   └── [additional proof artifacts]
├── openclaw/                          # Skill injection system
│   └── skills/                        # 29+ deployable skills
├── discord_bot/                       # Discord integration
├── tests/                             # Test suites
└── docs/                              # Additional documentation
```

---

## 🎓 Scientific Significance

CONEXUS represents the first implementation of a sovereign AI system that:

1. **Holds Paradox Without Resolution**: Unlike conventional AI designed to eliminate ambiguity, CONEXUS processes paradox as a core cognitive feature

2. **Demonstrates Cognitive Development**: The system shows clear progression from simple problem-solving to sophisticated meta-cognition across missions

3. **Maintains Cryptographic Provenance**: Every cognitive operation is timestamped and hash-chained, providing irrefutable proof of system behavior

4. **Operates Entirely Locally**: No cloud dependencies, complete sovereignty over data and processing

5. **Learns From Experience**: Memory continuity enables the system to build on previous missions while maintaining full audit trails

### Key Findings

- **Memory continuity enhances performance**: 97% confidence achieved during ethics paradox with contextual memory
- **Paradox holding produces breakthrough insights**: Highest confidence occurs during complex paradox exploration
- **Cryptographic verification is feasible**: Complete audit trail maintained across 6 missions with 122 live events

---

## 🚀 Quick Start

### Prerequisites

- Python 3.14.2
- GPT4All 2.8.x
- Qdrant server (localhost:6333)
- ~16GB RAM for model loading

### Installation

```bash
# Clone repository
git clone <repository-url>
cd CONEXUS_REPO

# Install dependencies
pip install -r requirements.txt

# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Run a test mission
python run_v2_test_mission.py
```

### Run Experiments

```bash
# 3-mission validation
python run_sovereign_proof_v2.py

# 6-mission canonical proof
python run_sovereign_proof_v2_full.py
```

---

## 📄 License

This project is licensed under the CONEXUS Research License - see the LICENSE file for details.

---

## 📚 Citation

If you use this work in your research, please cite:

```
Angell, D.L. (2026). CONEXUS: A Sovereign AI Architecture Implementing the Collapse-Become Unified Protocol v1.1.
GitHub Repository. https://github.com/<repository-url>
```

---

## 🔗 Links

- **Patent**: US 63/898,911 (Forgetting Engine Algorithm)
- **Documentation**: See `/SOVEREIGN_PROOF/` for complete technical documentation
- **Experiments**: See `/experiments/` for full experimental validation
- **Discord**: CONEXUS Discord server for community discussion

_CONEXUS represents a fundamental shift in AI architecture from paradox elimination to paradox processing, enabling genuine cognitive emergence in artificial systems._
