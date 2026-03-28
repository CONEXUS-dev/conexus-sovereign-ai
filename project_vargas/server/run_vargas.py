# Simple V4 Server - Your Customized OpenClaw Agent
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent.parent / "agent"))
sys.path.append(str(Path(__file__).parent.parent / "ecp"))

from vargas_agent_v4_complete import create_vargas_agent_v4_complete

def main():
    """Run V4 Customized OpenClaw Agent Server"""
    print("🚀 Vargas V4 Server - Your Customized OpenClaw Agent")
    print("🤖 ECP Architecture + 99 Semantic Skills")
    print("=" * 60)
    
    # Create agent
    agent = create_vargas_agent_v4_complete()
    
    print(f"✅ Agent initialized")
    print(f"✅ Available Skills: {len(agent.openclaw.get_available_skills())}")
    print(f"✅ ECP Architecture: Active")
    print(f"✅ Type 'quit' to exit")
    print("=" * 60)
    
    # Conversation loop
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'stop']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Process message
            result = agent.process_message(user_input)
            
            # Display response
            print(f"\n🤖 Vargas: {result['response']}")
            
            # Show ECP status
            ecp = result['ecp_status']
            print(f"🧠 ECP: Stage {ecp['substrate']['stage']}, Paradoxes: {ecp['substrate']['paradox_count']}")
            
            # Show skill executions
            if result['skills_executed']:
                print(f"🛠️ Skills: {len(result['skills_executed'])} executed")
                for skill in result['skills_executed']:
                    print(f"   - {skill['name']} (score: {skill['score']})")
            
            # Show context usage
            print(f"📊 Context: {result['context_used']:.0f} tokens")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
