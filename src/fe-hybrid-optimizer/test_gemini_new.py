"""
Test NEW google-genai package (modern API).
This should work without protobuf conflicts.
"""

print("=" * 60)
print("GEMINI NEW API TEST (google-genai package)")
print("=" * 60)

GEMINI_API_KEY = "AIzaSyC-TUJ78r2k2rl6G3OU-H8ulUNKb142i7M"

print("\n[TEST 1] Import new google-genai package...")
print("-" * 60)

try:
    from google import genai
    from google.genai import types
    print("✓ google-genai imported successfully")
except ImportError as e:
    print(f"✗ google-genai not installed: {e}")
    print("Run: pip install google-genai")
    exit(1)

print("\n[TEST 2] Configure and test basic API call...")
print("-" * 60)

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Say "Hello" if you can read this.'
    )
    
    print("✓ Basic API call successful!")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"✗ API call failed: {type(e).__name__}: {e}")
    exit(1)

print("\n[TEST 3] Test JSON response (pilot decision format)...")
print("-" * 60)

pilot_prompt = """You are a VRP optimization pilot. Return ONLY valid JSON with these exact keys:

{
  "keep_ids": ["c1", "c2", "c3"],
  "paradox_add_ids": ["c4"],
  "operator_mix_next": {"swap": 0.3, "relocate": 0.4, "reseed": 0.2, "pattern_injection": 0.1},
  "pattern_ops": [{"op": "CLUSTER_LOCK"}],
  "proto": {"moments": [{"g": 1, "type": "test", "note": "testing"}]},
  "rationale": {"survival_logic": "test", "paradox_logic": "test"}
}

CRITICAL: Return ONLY the JSON object. No explanation. No markdown. Just the JSON starting with { and ending with }"""

try:
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=pilot_prompt
    )
    
    print("✓ Pilot decision test successful!")
    print(f"Response length: {len(response.text)} chars")
    print(f"First 200 chars: {response.text[:200]}")
    
    # Try to parse as JSON
    import json
    
    # Clean response
    text = response.text.strip()
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        text = text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        text = text[start:end].strip()
    
    # Extract JSON
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1:
        text = text[first_brace:last_brace+1]
    
    data = json.loads(text)
    print(f"\n✓ JSON parsed successfully!")
    print(f"Keys: {list(data.keys())}")
    
except Exception as e:
    print(f"✗ Pilot decision test failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
print("\n✅ Gemini NEW API works!")
print("✅ Can generate pilot decisions in JSON format")
print("✅ FREE - No API costs!")
print("\nReady to create gemini_pilot_adapter.py as free alternative to Claude!")
