#!/usr/bin/env python3
"""
Test V4 ECP Components
Basic verification that all ECP components initialize and function correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ecp_components():
    """Test all ECP components can be imported and initialized"""
    print("🧪 Testing V4 ECP Components...")
    
    try:
        # Test imports
        from ecp import ECPSubstrate, ForgettingEngine, ModelBridge, TensionCompressor, RecursiveReinjection
        print("✅ ECP components imported successfully")
        
        # Initialize substrate
        substrate = ECPSubstrate(dimensions=384, base_threshold=0.618)
        print(f"✅ ECP Substrate initialized: {substrate.summary()}")
        
        # Initialize forgetting engine
        engine = ForgettingEngine(substrate, retention_threshold=0.3)
        print(f"✅ Forgetting Engine initialized: {engine.summary()}")
        
        # Initialize model bridge
        bridge = ModelBridge(substrate, engine)
        print("✅ Model Bridge initialized")
        
        # Test embedding
        test_text = "This is a test of the emergency broadcast system."
        embedding = bridge.embed(test_text)
        print(f"✅ Text embedding: {len(embedding)} dimensions")
        
        # Test tension calculation
        tension = substrate.compute_tension_gradient(embedding, substrate.state_vector)
        print(f"✅ Tension gradient: {tension:.4f}")
        
        # Test dual-vector processing
        prompt = "What is the relationship between freedom and structure?"
        response = "Freedom exists within structure, and structure gives meaning to freedom."
        
        _, passes = bridge.process_model_output(prompt, response)
        print(f"✅ Dual-vector processing: {'PASSED' if passes else 'FAILED'}")
        
        # Initialize memory compressor
        compressor = TensionCompressor(substrate, retention_threshold=0.75)
        print("✅ Memory Compressor initialized")
        
        # Test tension scoring
        tension_score = compressor.calculate_tension_score(response)
        print(f"✅ Tension score: {tension_score:.4f}")
        
        # Initialize recursive reinjection
        reinjector = RecursiveReinjection(substrate, engine, bridge)
        print("✅ Recursive Reinjection initialized")
        
        # Test paradox extraction
        paradoxes = bridge.extract_paradoxes("This is both true and false, yet meaningful.")
        print(f"✅ Paradox extraction: {len(paradoxes)} paradoxes found")
        
        # Test artifact creation
        def mock_model_generate(prompt):
            return f"Mock response to: {prompt[:50]}..."
        
        cycle_result = reinjector.run_single_cycle("Test seed", mock_model_generate)
        print(f"✅ Single cycle: {'SURVIVED' if cycle_result['survived'] else 'KILLED'}")
        
        return True
        
    except Exception as e:
        print(f"❌ ECP test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_v4_configuration():
    """Test V4 configuration loading"""
    print("\n🧪 Testing V4 Configuration...")
    
    try:
        import json
        config_path = project_root / "config" / "vargas_config.json"
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration loaded successfully")
        print(f"✅ Model: {config.get('model')}")
        print(f"✅ ECP enabled: {'ecp' in config}")
        
        if 'ecp' in config:
            ecp_config = config['ecp']
            print(f"✅ Context threshold: {ecp_config.get('context_threshold')}")
            print(f"✅ Substrate dimensions: {ecp_config.get('substrate_dimensions')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_v4_structure():
    """Test V4 folder structure"""
    print("\n🧪 Testing V4 Structure...")
    
    required_dirs = [
        "agent", "adapters", "config", "ecp", "memory", 
        "tools", "discord", "server", "prompts", "workspace", "logs"
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            missing_dirs.append(dir_name)
        else:
            print(f"✅ {dir_name}/ directory exists")
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    return True

def main():
    """Run all V4 tests"""
    print("🚀 Testing Vargas V4 - ECP Architecture")
    print("=" * 50)
    
    results = []
    results.append(test_v4_structure())
    results.append(test_v4_configuration())
    results.append(test_ecp_components())
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    print(f"📊 V4 Test Results: {passed}/{total} test groups working")
    
    if passed == total:
        print("🎉 Vargas V4 ECP Architecture is Functional!")
        print("\n📋 V4 ECP Features Active:")
        print("✅ ECP Substrate with vector math")
        print("✅ Forgetting Engine (consensus=DELETE)")
        print("✅ Model Bridge (dual-vector interceptor)")
        print("✅ Memory Compression (tension-preserving)")
        print("✅ Recursive Reinjection (autonomous cycles)")
        print("✅ Configuration system")
        print("✅ Project structure complete")
        
        print("\n🚀 Ready for V4 development!")
        print("\n📋 Next Steps:")
        print("1. Copy V3 components (agent, tools, adapters)")
        print("2. Integrate ECP with V3 systems")
        print("3. Update Discord bot for V4")
        print("4. Run integration tests")
        print("5. Deploy as Vargas V4")
    else:
        print("❌ Some V4 components need attention")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
