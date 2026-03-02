"""
Standalone Gemini API test - NO OR-Tools import to avoid protobuf conflict.
This tests Gemini in isolation to see if it works for pilot decisions.
"""

print("=" * 60)
print("GEMINI STANDALONE TEST (No OR-Tools)")
print("=" * 60)

# Your Gemini API key
GEMINI_API_KEY = "AIzaSyC-TUJ78r2k2rl6G3OU-H8ulUNKb142i7M"

print("\n[TEST 1] Import Gemini package...")
print("-" * 60)

try:
    import google.generativeai as genai
    print("✓ google-generativeai imported successfully")
except ImportError:
    print("✗ google-generativeai not installed")
    print("Run: pip install google-generativeai")
    exit(1)

print("\n[TEST 2] Configure and test basic API call...")
print("-" * 60)

try:
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Try gemini-1.5-flash (free tier model)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    response = model.generate_content("Say 'Hello' if you can read this.")
    print(f"✓ Basic API call successful!")
    print(f"Model: gemini-1.5-flash")
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
    response = model.generate_content(pilot_prompt)
    print(f"✓ Pilot decision test successful!")
    print(f"Response length: {len(response.text)} chars")
    print(f"First 200 chars: {response.text[:200]}")
    print(f"Last 100 chars: {response.text[-100:]}")
    
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
    exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
print("\n✅ Gemini API works in standalone mode!")
print("✅ Can generate pilot decisions in JSON format")
print("✅ FREE - No API costs!")
print("\nNext step: Create gemini_pilot_adapter.py as alternative to Claude")
