#!/usr/bin/env python3
"""
CONEXUS Discord Bot Integration Test
Tests the Discord bot integration with CONEXUS system
"""

import requests
import json
import sys

def test_gateway_connection():
    """Test connection to CONEXUS Gateway"""
    print("🔍 Testing Gateway connection...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Gateway online: {data.get('service', 'unknown')} v{data.get('version', 'unknown')}")
            return True
        else:
            print(f"❌ Gateway error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Gateway connection failed: {e}")
        return False

def test_qdrant_connection():
    """Test connection to Qdrant database"""
    print("🔍 Testing Qdrant connection...")
    try:
        response = requests.get("http://localhost:6333/collections/conexus_lineage", timeout=5)
        if response.status_code == 200:
            data = response.json()
            points = data['result']['points_count']
            print(f"✅ Qdrant online: {points} memory vectors stored")
            return True
        else:
            print(f"❌ Qdrant error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        return False

def test_task_submission():
    """Test task submission to Gateway"""
    print("🔍 Testing task submission...")
    try:
        task_data = {
            "task_input": "test integration command",
            "agent_assignment": "sway",
            "security_context": {
                "user_id": "test_user",
                "channel_id": "test_channel",
                "timestamp": "2026-02-22T13:55:00Z"
            }
        }
        
        response = requests.post("http://localhost:8000/tasks", json=task_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Task submitted: {data.get('status', 'unknown')}")
            print(f"📋 Task ID: {data.get('task_id', 'unknown')}")
            return True
        else:
            print(f"❌ Task submission failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Task submission error: {e}")
        return False

def test_discord_bot_files():
    """Test Discord bot file structure"""
    print("🔍 Testing Discord bot files...")
    
    required_files = [
        "bot.py",
        "requirements.txt",
        ".env",
        "start_bot.py",
        "README.md"
    ]
    
    import os
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

def main():
    """Run all integration tests"""
    print("🚀 CONEXUS Discord Bot Integration Test")
    print("=" * 50)
    
    tests = [
        ("Discord Bot Files", test_discord_bot_files),
        ("Gateway Connection", test_gateway_connection),
        ("Qdrant Connection", test_qdrant_connection),
        ("Task Submission", test_task_submission)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Discord bot ready for deployment.")
        return True
    else:
        print("⚠️ Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
