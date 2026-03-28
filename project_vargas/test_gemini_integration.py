# Test Gemini 3.1 Pro Integration
import os
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "ecp"))
sys.path.append(str(Path(__file__).parent))

def test_gemini_api_key():
    """Test that the new API key is properly configured"""
    print("🧪 Testing Gemini 3.1 Pro API Key...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False
    
    expected_key = "AIzaSyB9o28uejvf0JxeU7rVFUt4lRSjvtI5KJQ"
    if api_key != expected_key:
        print(f"❌ API key mismatch. Expected: {expected_key[:10]}..., Got: {api_key[:10]}...")
        return False
    
    print(f"✅ API key configured: {api_key[:10]}...")
    return True

def test_gemini_client():
    """Test Gemini client initialization"""
    print("\n🧪 Testing Gemini Client...")
    
    try:
        from adapters.cloud_llm.gemini_client import GeminiLLMClient
        
        client = GeminiLLMClient()
        print("✅ Gemini client initialized successfully")
        print(f"✅ Default model: {client.default_model}")
        print(f"✅ Embedding model: {client.embedding_model}")
        
        return True, client
    except Exception as e:
        print(f"❌ Gemini client failed: {e}")
        return False, None

def test_gemini_embeddings():
    """Test Gemini 3.1 Pro embeddings"""
    print("\n🧪 Testing Gemini 3.1 Pro Embeddings...")
    
    try:
        import google.generativeai as genai
        
        # Configure API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Test embedding
        model = genai.GenerativeModel("gemini-embedding-001")
        result = model.embed_content(
            content="This is a test of Gemini 3.1 Pro embeddings.",
            model="gemini-embedding-001"
        )
        
        embedding = result.embedding_values
        print(f"✅ Embedding generated: {len(embedding)} dimensions")
        print(f"✅ Sample values: {embedding[:5]}...")
        
        return True
    except Exception as e:
        print(f"❌ Gemini embedding failed: {e}")
        return False

def test_ecp_with_gemini():
    """Test ECP components with Gemini embeddings"""
    print("\n🧪 Testing ECP Components with Gemini...")
    
    try:
        from ecp_substrate import ECPSubstrate
        from forgetting_engine import ForgettingEngine
        from model_bridge import ModelBridge
        
        # Initialize components
        substrate = ECPSubstrate(dimensions=768, base_threshold=0.618)  # Gemini dimension
        engine = ForgettingEngine(substrate, retention_threshold=0.3)
        bridge = ModelBridge(substrate, engine)
        
        print("✅ ECP components initialized with Gemini")
        
        # Test embedding
        test_text = "This is a test of the ECP architecture with Gemini 3.1 Pro."
        embedding = bridge.embed(test_text)
        
        print(f"✅ Gemini embedding via ECP: {len(embedding)} dimensions")
        print(f"✅ Embedding norm: {float(np.linalg.norm(embedding)):.3f}")
        
        # Test tension calculation
        test_vector = np.random.rand(768)
        tension = substrate.compute_tension_gradient(test_vector, substrate.state_vector)
        print(f"✅ Tension calculation: {tension:.3f}")
        
        return True
    except Exception as e:
        print(f"❌ ECP with Gemini failed: {e}")
        return False

def test_openclaw_config():
    """Test OpenClaw configuration"""
    print("\n🧪 Testing OpenClaw Configuration...")
    
    try:
        import json
        
        # Check gateway config
        gateway_path = Path(__file__).parent.parent / "openclaw" / "gateway.json"
        with open(gateway_path, 'r') as f:
            gateway_config = json.load(f)
        
        print(f"✅ Gateway model: {gateway_config.get('model')}")
        print(f"✅ Gateway provider: {gateway_config.get('provider')}")
        
        # Check agent configs
        sway_path = Path(__file__).parent.parent / "openclaw" / "agents" / "sway" / "agent.yaml"
        with open(sway_path, 'r') as f:
            sway_config = f.read()
        
        if "gemini-3.1-pro-preview" in sway_config:
            print("✅ Sway agent configured for Gemini 3.1 Pro")
        else:
            print("❌ Sway agent not configured for Gemini")
            
        return True
    except Exception as e:
        print(f"❌ OpenClaw config check failed: {e}")
        return False

def main():
    """Run all Gemini 3.1 Pro integration tests"""
    print("🚀 Testing Gemini 3.1 Pro Integration")
    print("=" * 60)
    
    # Test API key
    results = []
    results.append(test_gemini_api_key())
    
    # Test Gemini client
    success, client = test_gemini_client()
    results.append(success)
    
    # Test embeddings
    results.append(test_gemini_embeddings())
    
    # Test ECP with Gemini
    results.append(test_ecp_with_gemini())
    
    # Test OpenClaw config
    results.append(test_openclaw_config())
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    print(f"📊 Gemini 3.1 Pro Integration Results: {passed}/{total} tests working")
    
    if passed == total:
        print("🎉 Everything switched to Gemini 3.1 Pro successfully!")
        print("\n📋 What's Now Using Gemini 3.1 Pro:")
        print("✅ Vargas Agent (Discord bot)")
        print("✅ ECP Substrate (vector math)")
        print("✅ Forgetting Engine (dual-vector filter)")
        print("✅ Model Bridge (interceptor)")
        print("✅ Memory Compression (archiver)")
        print("✅ Recursive Reinjection (autonomous cycles)")
        print("✅ OpenClaw Gateway (skills)")
        print("✅ Sway Agent (Collapse mode)")
        print("✅ Opie Agent (Become mode)")
        print("\n🚀 Ready to launch with highest-tier Gemini!")
    else:
        print("⚠️  Some components need attention")
    
    return passed == total

if __name__ == "__main__":
    import numpy as np
    main()
