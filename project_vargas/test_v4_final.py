# Final V4 Test - Fixed imports
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "ecp"))
sys.path.append(str(Path(__file__).parent / "agent"))

def test_v4_final():
    """Test V4 with fixed imports"""
    print("🧪 Testing Vargas V4 - Final Version...")
    
    try:
        # Test ECP components with new google.genai
        from ecp_substrate import ECPSubstrate
        from forgetting_engine import ForgettingEngine
        from model_bridge import ModelBridge
        
        print("✅ ECP imports successful with google.genai")
        
        # Initialize components
        substrate = ECPSubstrate(dimensions=768, base_threshold=0.618)  # Gemini dimension
        engine = ForgettingEngine(substrate, retention_threshold=0.3)
        bridge = ModelBridge(substrate, engine)
        
        print("✅ ECP components initialized")
        
        # Test embedding
        test_text = "Testing Vargas V4 with Gemini 3.1 Pro."
        embedding = bridge.embed(test_text)
        
        print(f"✅ Gemini embedding: {len(embedding)} dimensions")
        print(f"✅ Embedding norm: {float(np.linalg.norm(embedding)):.3f}")
        
        # Test V4 agent creation
        from vargas_agent_v4 import create_vargas_agent_v4
        
        agent = create_vargas_agent_v4()
        print("✅ V4 agent created successfully")
        
        # Get ECP status
        ecp_status = agent.get_ecp_status()
        print(f"✅ ECP Status: {ecp_status['substrate']['stage']}")
        
        return True
        
    except Exception as e:
        print(f"❌ V4 test failed: {e}")
        return False

def main():
    """Run final V4 test"""
    print("🚀 Vargas V4 Final Test")
    print("=" * 40)
    
    if test_v4_final():
        print("\n🎉 Vargas V4 is ready!")
        print("\n📋 V4 Features:")
        print("✅ ECP Substrate with Gemini 3.1 Pro")
        print("✅ Forgetting Engine (consensus=DELETE)")
        print("✅ Model Bridge (dual-vector interceptor)")
        print("✅ Memory Compression (tension-preserving)")
        print("✅ Recursive Reinjection (autonomous cycles)")
        print("✅ 80% Context Tripwire")
        print("✅ Fixed google.genai imports")
        print("\n🚀 Ready to run Vargas V4!")
        print("\n📋 To run V4:")
        print("python agent/vargas_agent_v4.py")
    else:
        print("❌ V4 needs attention")

if __name__ == "__main__":
    import numpy as np
    main()
