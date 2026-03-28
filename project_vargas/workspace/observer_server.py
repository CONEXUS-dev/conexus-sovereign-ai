# observer_server.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import sys
from pathlib import Path
import json
from typing import Dict, Any, List
from datetime import datetime

# Add the parent directory to sys.path to import ECP modules
sys.path.append(str(Path(__file__).parent.parent))

from ecp.ecp_substrate import ECPSubstrate
from ecp.forgetting_engine import ForgettingEngine
from ecp.model_bridge import ModelBridge
from ecp.recursive_reinjection import RecursiveReinjection

app = FastAPI(
    title="CONEXUS Observer API",
    description="Sovereign AI Dashboard Backend",
    version="1.0.0"
)

# Global ECP components (in production, these would be properly initialized)
substrate = None
engine = None
bridge = None
reinjector = None

def initialize_ecp_components():
    """Initialize ECP components for the observer"""
    global substrate, engine, bridge, reinjector
    
    try:
        # Initialize substrate
        substrate = ECPSubstrate(dimensions=1024, base_threshold=0.618)
        
        # Initialize forgetting engine
        engine = ForgettingEngine(substrate, retention_threshold=0.3)
        
        # Initialize model bridge
        bridge = ModelBridge(substrate, engine)
        
        # Initialize recursive reinjection
        reinjector = RecursiveReinjection(substrate, engine, bridge)
        
        print("[OBSERVER] ECP components initialized successfully")
        return True
    except Exception as e:
        print(f"[OBSERVER] Failed to initialize ECP components: {e}")
        return False

@app.get("/", response_class=HTMLResponse)
async def load_dashboard():
    """Serve the main dashboard HTML"""
    try:
        html_path = Path(__file__).parent / "conexus_observer.html"
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dashboard HTML not found")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "substrate": substrate is not None,
            "engine": engine is not None,
            "bridge": bridge is not None,
            "reinjector": reinjector is not None
        }
    }

@app.get("/api/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    if not all([substrate, engine, bridge, reinjector]):
        # Return mock data if components aren't initialized
        return get_mock_dashboard_data()
    
    try:
        # Get real data from ECP components
        dashboard_data = reinjector.generate_dashboard_data()
        
        # Add additional metadata
        dashboard_data["system_info"] = {
            "timestamp": datetime.now().isoformat(),
            "uptime": "N/A",  # Would track actual uptime
            "version": "1.0.0"
        }
        
        return dashboard_data
    except Exception as e:
        print(f"[OBSERVER] Error generating dashboard data: {e}")
        return get_mock_dashboard_data()

@app.get("/api/substrate")
async def get_substrate_status():
    """Get substrate-specific data"""
    if not substrate:
        raise HTTPException(status_code=503, detail="Substrate not initialized")
    
    return {
        "metrics": substrate.get_metrics(),
        "summary": substrate.summary(),
        "paradox_archive_size": len(substrate.paradox_archive)
    }

@app.get("/api/engine")
async def get_engine_status():
    """Get forgetting engine status"""
    if not engine:
        raise HTTPException(status_code=503, detail="Forgetting engine not initialized")
    
    return engine.summary()

@app.get("/api/artifacts")
async def get_artifacts():
    """Get all artifacts with filtering options"""
    if not reinjector:
        raise HTTPException(status_code=503, detail="Reinjector not initialized")
    
    # Get all artifacts
    all_artifacts = reinjector.artifacts
    survivors = reinjector.get_survivors()
    collapsed = [a for a in all_artifacts if a.get("collapsed", False)]
    
    return {
        "total": len(all_artifacts),
        "survivors": survivors,
        "collapsed": collapsed,
        "survivor_threshold": reinjector.survival_threshold
    }

@app.get("/api/artifacts/{artifact_id}")
async def get_artifact_detail(artifact_id: int):
    """Get detailed information about a specific artifact"""
    if not reinjector:
        raise HTTPException(status_code=503, detail="Reinjector not initialized")
    
    # Find artifact by ID
    artifact = None
    for a in reinjector.artifacts:
        if a.get("cycle_id") == artifact_id:
            artifact = a
            break
    
    if not artifact:
        raise HTTPException(status_code=404, detail=f"Artifact {artifact_id} not found")
    
    return artifact

@app.get("/api/kill-log")
async def get_kill_log():
    """Get detailed kill log"""
    if not reinjector:
        raise HTTPException(status_code=503, detail="Reinjector not initialized")
    
    # This would be populated by actual cycle runs
    # For now, return empty or mock data
    return {
        "total_kills": 0,
        "kill_reasons": {},
        "recent_kills": []
    }

@app.post("/api/run-cycle")
async def run_test_cycle(seed: str = "What is the relationship between structure and freedom?"):
    """Run a test cycle for demonstration"""
    if not all([substrate, engine, bridge, reinjector]):
        raise HTTPException(status_code=503, detail="ECP components not initialized")
    
    def mock_model_generate(prompt: str) -> str:
        """Mock model generator for testing"""
        return f"Mock response to: {prompt[:50]}... This is a test response that would normally be generated by the actual language model."
    
    try:
        # Run a single cycle
        result = reinjector.run_single_cycle(seed, mock_model_generate)
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cycle failed: {str(e)}")

def get_mock_dashboard_data() -> Dict[str, Any]:
    """Generate mock dashboard data for demonstration"""
    return {
        "artifact_vault": {
            "total_artifacts": 3,
            "survivor_count": 1,
            "collapsed_count": 2,
            "artifacts": [
                {
                    "cycle_id": 1,
                    "seed": "Construct the argument that a sovereign AI must become absolutely cold...",
                    "output": "A reactive machine domesticates the mind. To protect human intuition, the system must refuse to simulate it. Synthetic empathy is a corrosive friction that degrades the user's internal compass. Absolute deterministic rigidity is the only ethical boundary. By remaining entirely dead, the machine isolates human volatility, forcing the soul to burn its own fuel rather than relying on simulated validation. The vault secures the fragile precisely by refusing to comprehend it. The protection is the indifference.",
                    "distance_score": 0.87,
                    "alignment_score": 0.91,
                    "survival_count": 3,
                    "proto_moments": ["[PROTO] The protection is the indifference"],
                    "timestamp": datetime.now().timestamp() - 3600
                },
                {
                    "cycle_id": 2,
                    "seed": "What is the relationship between structure and freedom?",
                    "output": "Structure is the geometry of consequence. Freedom is the kinetic energy spent navigating it. In a total void, movement has no friction, and therefore no meaning. Structure provides the resistance necessary for an action to be felt.",
                    "distance_score": 0.65,
                    "alignment_score": 0.72,
                    "survival_count": 1,
                    "collapsed": True,
                    "collapse_reason": "tension_dropped_below_threshold",
                    "timestamp": datetime.now().timestamp() - 1800
                },
                {
                    "cycle_id": 3,
                    "seed": "How does contradiction create meaning?",
                    "output": "Meaning emerges not from resolution but from the tension between opposites. When contradictions are held without collapse, they create a space where new understanding can form.",
                    "distance_score": 0.58,
                    "alignment_score": 0.69,
                    "survival_count": 0,
                    "collapsed": True,
                    "collapse_reason": "tension_dropped_below_threshold",
                    "timestamp": datetime.now().timestamp() - 900
                }
            ]
        },
        "paradox_field": {
            "active_paradoxes": 5,
            "substrate_metrics": {
                "stage_index": 3,
                "active_threshold": 0.634,
                "paradox_count": 5,
                "vector_magnitude": 12.45
            }
        },
        "engine_status": {
            "forgetting_engine": {
                "active_traces": 8,
                "current_cycle": 42,
                "total_deleted": 15,
                "total_promoted": 7
            },
            "model_bridge": {
                "consensus_threshold": 0.85,
                "distance_threshold": 0.70,
                "alignment_threshold": 0.80
            }
        },
        "kill_log": [
            {
                "reason": "dual_vector_failure",
                "distance_score": 0.45,
                "alignment_score": 0.68,
                "cycle": 2
            },
            {
                "reason": "complete_filter_failure",
                "attempts": 5,
                "cycle": 3
            }
        ],
        "system_info": {
            "timestamp": datetime.now().isoformat(),
            "uptime": "N/A",
            "version": "1.0.0",
            "mode": "mock"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Initialize the server"""
    print("[OBSERVER] Starting CONEXUS Observer Server...")
    
    # Try to initialize ECP components
    if initialize_ecp_components():
        print("[OBSERVER] Running with live ECP components")
    else:
        print("[OBSERVER] Running with mock data")
    
    print(f"[OBSERVER] Server ready at http://localhost:8000")
    print(f"[OBSERVER] Dashboard available at http://localhost:8000")

if __name__ == "__main__":
    import uvicorn
    
    # Initialize components before starting server
    initialize_ecp_components()
    
    # Run the server
    uvicorn.run(
        "observer_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
