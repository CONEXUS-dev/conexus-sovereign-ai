#!/usr/bin/env python3
"""
CONEXUS Discord Bot Startup Script
Starts the Discord bot for CONEXUS sovereign AI system
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN or DISCORD_TOKEN == "YOUR_DISCORD_TOKEN_HERE":
    print("❌ Error: DISCORD_TOKEN not found in .env file")
    print("Please edit the .env file and add your Discord bot token")
    sys.exit(1)

# Check if CONEXUS Gateway is running
import requests
import time

def check_gateway():
    """Check if CONEXUS Gateway is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ CONEXUS Gateway is running")
            return True
        else:
            print("⚠️ CONEXUS Gateway responding but with issues")
            return False
    except requests.exceptions.RequestException:
        print("❌ CONEXUS Gateway is not running")
        print("Please start the Gateway service first:")
        print("cd C:\\Users\\Derek Angell\\Desktop\\CONEXUS_REPO\\golden-path\\verification")
        print("python minimal-gateway.py")
        return False

def check_qdrant():
    """Check if Qdrant database is running"""
    try:
        response = requests.get("http://localhost:6333/collections/conexus_lineage", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Qdrant database running with {data['result']['points_count']} memory vectors")
            return True
        else:
            print("⚠️ Qdrant responding but with issues")
            return False
    except requests.exceptions.RequestException:
        print("❌ Qdrant database is not running")
        print("Please start Qdrant first")
        return False

def main():
    """Main startup function"""
    print("🚀 Starting CONEXUS Discord Bot...")
    print("=" * 50)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    
    if not check_gateway():
        print("\n❌ Cannot start bot without Gateway service")
        return False
    
    if not check_qdrant():
        print("\n⚠️ Bot can start but Qdrant features will be limited")
    
    print("\n✅ Dependencies checked")
    print("🤖 Starting Discord bot...")
    
    # Import and start bot
    try:
        from bot import bot
        print("📡 Connecting to Discord...")
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
