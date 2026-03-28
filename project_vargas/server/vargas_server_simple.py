# Simple V4 Server - Your Customized OpenClaw Agent
import asyncio
import logging
import json
from pathlib import Path
import sys

# Add paths
sys.path.append(str(Path(__file__).parent.parent / "agent"))
sys.path.append(str(Path(__file__).parent.parent / "ecp"))

from vargas_agent_v4_complete import create_vargas_agent_v4_complete

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("vargas.server")

class SimpleVargasServer:
    """Simple persistent server for V4 Customized OpenClaw Agent"""
    
    def __init__(self):
        self.agent = create_vargas_agent_v4_complete()
        self.conversation_history = []
        self.session_id = f"session_{int(asyncio.get_event_loop().time())}"
        self.is_running = False
        
    async def start_server(self):
        """Start the persistent V4 server"""
        self.is_running = True
        self.session_id = f"session_{int(asyncio.get_event_loop().time())}"
        
        logger.info("🚀 Starting Vargas V4 Server")
        logger.info(f"🔑 Session: {self.session_id}")
        logger.info("🧠 ECP Architecture: Active")
        skills_count = len(self.agent.openclaw.get_available_skills())
        logger.info(f"🛠️ OpenClaw Skills: {skills_count} available")
        
        print("\n" + "="*60)
        print("🤖 VARGAS V4 - Your Customized OpenClaw Agent")
        print("📋 Type 'quit' to stop, or just type your message")
        print("="*60)
        
        # Server loop
        try:
            while self.is_running:
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'stop']:
                    await self.stop_server()
                    break
                
                # Process message
                try:
                    result = self.agent.process_message(user_input)
                    
                    # Display response
                    print(f"\n🤖 Vargas: {result['response']}")
                    
                    # Show ECP status
                    ecp = result['ecp_status']
                    print(f"🧠 ECP: Stage {ecp['substrate']['stage']}, Paradoxes: {ecp['substrate']['paradox_count']}")
                    
                    # Show skill executions
                    if result['skills_executed']:
                        print(f"🛠️ Skills: {len(result['skills_executed')} executed")
                        for skill in result['skills_executed']:
                            print(f"   - {skill['name']} (score: {skill['score']})")
                    
                    # Show context usage
                    print(f"📊 Context: {result['context_used']:.0f} tokens")
                    
                    # Store in conversation history
                    self.conversation_history.append({
                        "user": user_input,
                        "vargas": result['response'],
                        "timestamp": asyncio.get_event_loop().time(),
                        "ecp_status": result['ecp_status'],
                        "skills_executed": result['skills_executed']
                    })
                    
                except Exception as e:
                    logger.error(f"❌ Processing error: {e}")
                    print(f"❌ Error: {e}")
                    
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user")
        except Exception as e:
            logger.error(f"❌ Server error: {e}")
    
    async def stop_server(self):
        """Stop the server"""
        self.is_running = False
        logger.info("🛑 Shutting down Vargas V4 Server")
        
        # Save conversation history
        if self.conversation_history:
            history_file = Path(__file__).parent / f"conversation_history_{self.session_id}.json"
            with open(history_file, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
            logger.info(f"💾 Conversation history saved to {history_file}")
        
        print("\n👋 Goodbye! Vargas V4 Server shutting down.")
        
        # Show final stats
        if self.conversation_history:
            print(f"\n📊 Final Stats:")
            print(f"  Messages: {len(self.conversation_history)}")
            print(f"  Session: {self.session_id}")
            
            # Get final ECP status
            final_status = self.agent.get_ecp_status()
            print(f"  Final Stage: {final_status['substrate']['stage']}")
            print(f"  Final Paradoxes: {final_status['substrate']['paradox_count']}")

async def main():
    """Main entry point"""
    print("🚀 Vargas V4 Simple Server")
    print("🤖 Your Customized OpenClaw Agent")
    print("🧠 ECP Architecture + 99 Semantic Skills")
    print("=" * 50)
    
    # Create and start server
    server = SimpleVargasServer()
    await server.start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
