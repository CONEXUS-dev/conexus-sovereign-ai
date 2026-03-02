"""
Test script to debug Claude API calibration issue.
This will help us see exactly what's happening with the API calls.
"""

from pilot_adapter import PilotAdapter, llm_chat_call_placeholder

print("=" * 60)
print("CLAUDE API CALIBRATION DEBUG TEST")
print("=" * 60)

# Test 1: Simple API call
print("\n[TEST 1] Testing basic Claude API call...")
print("-" * 60)

try:
    test_messages = [
        {"role": "user", "content": "Say 'Hello' if you can read this."}
    ]
    
    response = llm_chat_call_placeholder(test_messages)
    print(f"✓ Basic API call successful!")
    print(f"Response: {response}")
    
except Exception as e:
    print(f"✗ Basic API call failed: {e}")
    print("\nThis suggests the Claude API key or connection has an issue.")
    exit(1)

# Test 2: Calibration with full protocol
print("\n[TEST 2] Testing full calibration...")
print("-" * 60)

try:
    pilot = PilotAdapter(mode="llm", llm_chat_fn=llm_chat_call_placeholder)
    pilot.calibrate()
    
    print(f"✓ Calibration successful!")
    print(f"Protocol: {pilot.protocol}")
    print(f"Pilot mode: {pilot.pilot_mode}")
    
except Exception as e:
    print(f"✗ Calibration failed: {e}")
    print("\nCheck the debug output above to see where it failed.")
    exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
print("\nClaude API is working correctly. You can now run the full validation.")
