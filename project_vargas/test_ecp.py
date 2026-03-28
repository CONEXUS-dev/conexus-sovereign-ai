# Test script for ECP components
import sys
import numpy as np
from pathlib import Path

# Add ECP directory to path
sys.path.append(str(Path(__file__).parent / "ecp"))

def test_ecp_substrate():
    """Test the ECP substrate with vector math"""
    print("Testing ECP Substrate...")
    
    try:
        from ecp_substrate import ECPSubstrate
        
        substrate = ECPSubstrate(dimensions=384, base_threshold=0.618)
        
        # Test vector creation
        test_vector = np.random.rand(384)
        state, tension = substrate.process_stage(test_vector)
        
        print(f"✅ Substrate initialized: dimensions={substrate.dimensions}, threshold={substrate.threshold}")
        print(f"✅ Process stage: tension={tension:.3f}, state_vector_norm={np.linalg.norm(state):.3f}")
        print(f"✅ Summary: {substrate.summary()}")
        
        return True
    except Exception as e:
        print(f"❌ Substrate failed: {e}")
        return False

def test_forgetting_engine():
    """Test the forgetting engine with inverted logic"""
    print("\nTesting Forgetting Engine...")
    
    try:
        from ecp_substrate import ECPSubstrate
        from forgetting_engine import ForgettingEngine
        
        substrate = ECPSubstrate(dimensions=384)
        engine = ForgettingEngine(substrate, retention_threshold=0.3)
        
        # Test signal processing
        test_vector = np.random.rand(384)
        engine.process_signal(test_vector)
        
        summary = engine.summary()
        print(f"✅ Engine initialized: retention_threshold={engine.retention_threshold}")
        print(f"✅ Summary: {summary}")
        
        return True
    except Exception as e:
        print(f"❌ Engine failed: {e}")
        return False

def test_model_bridge():
    """Test the model bridge interceptor"""
    print("\nTesting Model Bridge...")
    
    try:
        from ecp_substrate import ECPSubstrate
        from forgetting_engine import ForgettingEngine
        from model_bridge import ModelBridge
        
        substrate = ECPSubstrate(dimensions=384)
        engine = ForgettingEngine(substrate)
        bridge = ModelBridge(substrate, engine)
        
        # Test embedding
        test_text = "This is a test contradiction."
        embedding = bridge.embed(test_text)
        
        print(f"✅ Bridge initialized: embedding_dim={len(embedding)}")
        print(f"✅ Embedding norm: {np.linalg.norm(embedding):.3f}")
        
        return True
    except Exception as e:
        print(f"❌ Bridge failed: {e}")
        return False

def main():
    """Run all ECP component tests"""
    print("🧪 Testing ECP Architecture Components")
    print("=" * 50)
    
    results = []
    results.append(test_ecp_substrate())
    results.append(test_forgetting_engine())
    results.append(test_model_bridge())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    print(f"📊 Test Results: {passed}/{total} components working")
    
    if passed == total:
        print("🎉 All ECP components are functional!")
        print("\n📋 Next steps:")
        print("1. Install dependencies: pip install numpy sentence-transformers")
        print("2. Test the dashboard: python workspace/observer_server.py")
        print("3. Integrate with Vargas agent")
    else:
        print("⚠️  Some components need attention")
    
    return passed == total

if __name__ == "__main__":
    main()
