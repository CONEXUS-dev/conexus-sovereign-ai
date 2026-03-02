"""Test script to list available Claude models."""
import anthropic
import os

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("Please set ANTHROPIC_API_KEY environment variable")

client = anthropic.Anthropic(api_key=api_key)

print("Querying available Claude models...")
print("=" * 60)

try:
    models = client.models.list()
    print(f"\nAvailable models: {models}")
    print("\nModel details:")
    for model in models.data:
        print(f"  - {model.id}")
except Exception as e:
    print(f"Error listing models: {e}")
    print("\nTrying to call API with test models...")
    
    # Try each model to see which works
    test_models = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-latest",
        "claude-3-5-sonnet-20240620",
        "claude-3-sonnet-20240229",
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307"
    ]
    
    for model_name in test_models:
        try:
            response = client.messages.create(
                model=model_name,
                max_tokens=100,
                messages=[{"role": "user", "content": "Say 'OK' if you can read this."}]
            )
            print(f"✓ {model_name} - WORKS!")
            print(f"  Response: {response.content[0].text}")
            break
        except Exception as e:
            print(f"✗ {model_name} - {str(e)[:80]}")
