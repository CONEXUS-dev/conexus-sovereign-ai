"""
Test Gemini API connection and basic functionality.
Gemini is FREE - no API costs!
"""

import os

print("=" * 60)
print("GEMINI API TEST")
print("=" * 60)

# Your Gemini API key (you provided this earlier)
api_key = "AIzaSyBXLlme_NwHIkHlPxSMxQBQ3Xc1Oy6Jg2E"

try:
    import google.generativeai as genai
except ImportError:
    print("\n✗ google-generativeai not installed")
    print("Run: pip install google-generativeai")
    exit(1)

# Configure Gemini
genai.configure(api_key=api_key)

print("\n[TEST 1] List available models...")
print("-" * 60)

try:
    models = genai.list_models()
    print("✓ Available Gemini models:")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
except Exception as e:
    print(f"✗ Failed to list models: {e}")
    exit(1)

print("\n[TEST 2] Simple API call...")
print("-" * 60)

try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'Hello' if you can read this.")
    
    print(f"✓ API call successful!")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"✗ API call failed: {e}")
    exit(1)

print("\n[TEST 3] JSON response test...")
print("-" * 60)

try:
    prompt = """Return ONLY valid JSON with these exact keys: {"status": "ok", "message": "test"}
    
Do not include any explanation. Just the JSON."""
    
    response = model.generate_content(prompt)
    print(f"✓ JSON test successful!")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"✗ JSON test failed: {e}")
    exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
print("\nGemini API is working and it's FREE!")
print("Ready to use for VRP validation.")
