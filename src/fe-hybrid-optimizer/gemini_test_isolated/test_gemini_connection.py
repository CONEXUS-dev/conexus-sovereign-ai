"""
TEST 1: Gemini API Connection Test
===================================
NEW API Key: AIzaSyCgFgJbf2f33u94VQtCnTkOhbT5gYzfuXI
Package: google-genai (modern package)

This test will:
1. Import the google-genai package
2. List ALL available models
3. Try EACH model until one works
4. Print detailed results for each attempt

NO OR-Tools imports - completely isolated test.
"""

import sys

print("=" * 80)
print("GEMINI API CONNECTION TEST - ISOLATED")
print("=" * 80)

GEMINI_API_KEY = "AIzaSyCgFgJbf2f33u94VQtCnTkOhbT5gYzfuXI"

# ============================================================================
# STEP 1: Import google-genai package
# ============================================================================
print("\n[STEP 1] Importing google-genai package...")
print("-" * 80)

try:
    from google import genai
    print("✓ google-genai imported successfully")
    print(f"  Package location: {genai.__file__}")
except ImportError as e:
    print(f"✗ FAILED to import google-genai: {e}")
    print("\nTo install, run:")
    print("  pip install google-genai")
    sys.exit(1)

# ============================================================================
# STEP 2: Initialize client
# ============================================================================
print("\n[STEP 2] Initializing Gemini client...")
print("-" * 80)

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    print("✓ Client initialized successfully")
except Exception as e:
    print(f"✗ FAILED to initialize client: {type(e).__name__}: {e}")
    sys.exit(1)

# ============================================================================
# STEP 3: List ALL available models
# ============================================================================
print("\n[STEP 3] Listing ALL available models...")
print("-" * 80)

try:
    models_response = client.models.list()
    
    # Extract model names
    model_names = []
    print("\nAvailable models:")
    for i, model in enumerate(models_response.models, 1):
        model_name = model.name
        if model_name.startswith('models/'):
            model_name = model_name.replace('models/', '')
        model_names.append(model_name)
        print(f"  {i}. {model_name}")
        print(f"     Display name: {model.display_name}")
        print(f"     Description: {model.description[:100]}..." if len(model.description) > 100 else f"     Description: {model.description}")
        print()
    
    print(f"\n✓ Found {len(model_names)} models")
    
except Exception as e:
    print(f"✗ FAILED to list models: {type(e).__name__}: {e}")
    print("\nTrying to continue with common model names...")
    model_names = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-2.0-flash-exp',
        'gemini-pro',
        'gemini-flash',
    ]

# ============================================================================
# STEP 4: Test EACH model with simple prompt
# ============================================================================
print("\n[STEP 4] Testing EACH model with simple prompt...")
print("-" * 80)

test_prompt = 'Say "Hello from Gemini!" if you can read this.'
working_models = []

for i, model_name in enumerate(model_names, 1):
    print(f"\n[Test {i}/{len(model_names)}] Trying model: {model_name}")
    print("-" * 40)
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=test_prompt
        )
        
        response_text = response.text
        print(f"✓ SUCCESS!")
        print(f"  Response: {response_text[:200]}")
        working_models.append(model_name)
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"✗ FAILED: {error_type}")
        print(f"  Error: {error_msg[:200]}")

# ============================================================================
# STEP 5: Summary
# ============================================================================
print("\n" + "=" * 80)
print("CONNECTION TEST SUMMARY")
print("=" * 80)

if working_models:
    print(f"\n✓ SUCCESS! Found {len(working_models)} working model(s):")
    for model in working_models:
        print(f"  - {model}")
    
    print(f"\n✅ RECOMMENDED MODEL: {working_models[0]}")
    print("\nNext steps:")
    print("  1. Use this model for calibration test")
    print("  2. Test CONEXUS-STEEL-04 protocol")
    print("  3. Test VRP optimization")
    
else:
    print("\n✗ NO WORKING MODELS FOUND")
    print("\nPossible issues:")
    print("  1. API key invalid or expired")
    print("  2. API not enabled for your account")
    print("  3. Network/firewall issues")
    print("  4. Model names changed")
    
    print("\nTo debug:")
    print("  - Check API key at: https://aistudio.google.com/apikey")
    print("  - Verify API is enabled")
    print("  - Try in browser: https://aistudio.google.com/")

print("\n" + "=" * 80)
