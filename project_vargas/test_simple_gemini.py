# Simple Gemini 3.1 Pro Test
import os
from pathlib import Path

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

def test_api_key():
    """Test API key loading"""
    api_key = os.getenv("GEMINI_API_KEY")
    expected_key = "AIzaSyB9o28uejvf0JxeU7rVFUt4lRSjvtI5KJQ"
    
    print(f"🔑 API Key: {api_key[:10] if api_key else 'None'}...")
    print(f"✅ Expected: {expected_key[:10]}...")
    print(f"✅ Match: {api_key == expected_key if api_key else False}")
    
    return api_key == expected_key

if __name__ == "__main__":
    print("🧪 Testing Gemini 3.1 Pro API Key")
    print("=" * 40)
    
    if test_api_key():
        print("🎉 API key configured correctly!")
    else:
        print("❌ API key issue detected")
