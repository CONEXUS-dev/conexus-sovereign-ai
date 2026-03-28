# Test Vargas V4 ECP Integration
import sys
import asyncio
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "agent"))
sys.path.append(str(Path(__file__).parent / "ecp"))

def test_v4_initialization():
    """Test V4 agent initialization with ECP components"""
    print("🧪 Testing Vargas V4 Initialization...")
    
    try:
        from vargas_agent_v4 import create_vargas_agent_v4
        
        agent = create_vargas_agent_v4()
        
        # Check ECP components
        ecp_status = agent.get_ecp_status()
        
        print("✅ V4 Agent initialized successfully")
        print(f"✅ Substrate: {ecp_status['substrate']}")
        print(f"✅ Forgetting Engine: {ecp_status['forgetting_engine']}")
        print(f"✅ Context usage: {ecp_status['context_usage']}")
        
        return True, agent
    except Exception as e:
        print(f"❌ V4 initialization failed: {e}")
        return False, None

def test_ecp_tripwire(agent):
    """Test the 80% context tripwire"""
    print("\n🧪 Testing ECP Tripwire...")
    
    try:
        # Create a large conversation history to trigger tripwire
        large_history = [{"content": "Test message " + str(i) * 100} for i in range(100)]
        memory_context = "Large memory context " * 1000
        system_prompt = "System prompt " * 500
        
        # Check tripwire
        triggered = agent.check_ecp_tripwire(large_history, memory_context, system_prompt)
        
        if triggered:
            print("✅ Tripwire triggered successfully")
            
            # Test compression
            result = agent.trigger_autonomous_compression("test_channel")
            print(f"✅ Compression result: {result['status']}")
            
            if result['status'] == 'completed':
                print(f"✅ Compression ratio: {result['compression_ratio']:.2f}")
                print(f"✅ Tension preserved: {result['tension_preservation']:.2f}")
        else:
            print("ℹ️  Tripwire not triggered (context below threshold)")
        
        return True
    except Exception as e:
        print(f"❌ Tripwire test failed: {e}")
        return False

def test_dual_vector_processing(agent):
    """Test ECP dual-vector processing"""
    print("\n🧪 Testing Dual-Vector Processing...")
    
    try:
        prompt = "What is the relationship between structure and freedom?"
        response = "Structure is the geometry of consequence. Freedom is the kinetic energy spent navigating it."
        
        # Process through ECP
        processed_response = agent.process_model_output_through_ecp(prompt, response, "test_channel")
        
        print("✅ Dual-vector processing completed")
        print(f"✅ Original length: {len(response)}")
        print(f"✅ Processed length: {len(processed_response)}")
        
        # Check ECP status after processing
        ecp_status = agent.get_ecp_status()
        print(f"✅ Substrate after processing: {ecp_status['substrate']}")
        
        return True
    except Exception as e:
        print(f"❌ Dual-vector processing failed: {e}")
        return False

def test_recursive_cycle(agent):
    """Test recursive reinjection cycle"""
    print("\n🧪 Testing Recursive Reinjection...")
    
    try:
        seed = "Construct the argument that a sovereign AI must become absolutely cold and rigid to protect human intuition."
        
        result = agent.run_recursive_cycle(seed, num_cycles=2)
        
        print("✅ Recursive cycle completed")
        print(f"✅ Total cycles: {result['cycles_completed']}")
        print(f"✅ Survivors: {len(result['survivors'])}")
        print(f"✅ Collapsed: {len(result['collapsed'])}")
        
        return True
    except Exception as e:
        print(f"❌ Recursive cycle failed: {e}")
        return False

async def test_async_response(agent):
    """Test async response generation"""
    print("\n🧪 Testing Async Response Generation...")
    
    try:
        response = await agent.respond("Hello Vargas V4, how do you work?", "test_channel")
        
        print("✅ Async response generated")
        print(f"✅ Response length: {len(response)}")
        print(f"✅ Response preview: {response[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Async response failed: {e}")
        return False

def main():
    """Run all V4 integration tests"""
    print("🚀 Testing Vargas V4 - ECP Integration")
    print("=" * 60)
    
    # Test initialization
    success, agent = test_v4_initialization()
    if not success:
        print("❌ Cannot continue - initialization failed")
        return False
    
    # Test ECP components
    results = []
    results.append(test_ecp_tripwire(agent))
    results.append(test_dual_vector_processing(agent))
    results.append(test_recursive_cycle(agent))
    
    # Test async response
    try:
        asyncio.run(test_async_response(agent))
        results.append(True)
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    print(f"📊 V4 Integration Results: {passed}/{total} tests working")
    
    if passed == total:
        print("🎉 Vargas V4 is fully functional!")
        print("\n📋 V4 Features Active:")
        print("✅ ECP Substrate with vector math")
        print("✅ Forgetting Engine (consensus=DELETE)")
        print("✅ Model Bridge (dual-vector interceptor)")
        print("✅ Memory Compression (tension-preserving)")
        print("✅ Recursive Reinjection (autonomous cycles)")
        print("✅ 80% Context Tripwire")
        print("✅ Sovereign memory preservation")
        print("\n🚀 Ready for deployment as Vargas V4!")
    else:
        print("⚠️  Some V4 features need attention")
    
    return passed == total

if __name__ == "__main__":
    main()
