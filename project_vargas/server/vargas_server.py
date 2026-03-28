# Vargas V4 Persistent Server - Your Customized OpenClaw Agent
import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional
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

class VargasServer:
    """Persistent server for Vargas V4 Customized OpenClaw Agent"""
    
    def __init__(self):
        self.agent = create_vargas_agent_v4_complete()
        self.conversation_history = []
        self.session_id = None
        self.is_running = False
        
    async def start_server(self, host: str = "localhost", port: int = 8080):
        """Start the persistent Vargas server"""
        self.is_running = True
        self.session_id = f"session_{int(asyncio.get_event_loop().time())}"
        
        logger.info("🚀 Starting Vargas V4 Server")
        logger.info(f"📡 Host: {host}:{port}")
        logger.info(f"🔑 Session: {self.session_id}")
        logger.info("🧠 ECP Architecture: Active")
        logger.info(f"🛠️ OpenClaw Skills: {len(self.agent.openclaw.get_available_skills())} available")
        
        # Server loop
        try:
            while self.is_running:
                print("\n" + "="*60)
                print("🤖 VARGAS V4 - Your Customized OpenClaw Agent")
                print("📋 Commands: 'message', 'status', 'skills', 'help', 'quit'")
                print("="*60)
                
                # Get user input
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Process commands
                if user_input.lower() in ['quit', 'exit', 'stop']:
                    await self.stop_server()
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                elif user_input.lower() == 'status':
                    self.show_status()
                elif user_input.lower() == 'skills':
                    self.show_skills()
                elif user_input.lower().startswith('message:'):
                    # Remove 'message:' prefix
                    message = user_input[8:].strip()
                    await self.process_message(message)
                else:
                    # Default: treat as message
                    await self.process_message(user_input)
                    
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user")
        except Exception as e:
            logger.error(f"❌ Server error: {e}")
    
    async def process_message(self, user_input: str):
        """Process user message through V4 agent"""
        print(f"\n📥 Processing: {user_input}")
        
        try:
            # Process through V4 agent
            result = self.agent.process_message(user_input)
            
            # Store in conversation history
            self.conversation_history.append({
                "user": user_input,
                "vargas": result["response"],
                "timestamp": asyncio.get_event_loop().time(),
                "ecp_status": result["ecp_status"],
                "skills_executed": result["skills_executed"]
            })
            
            # Display response
            print(f"\n🤖 Vargas: {result['response']}")
            
            # Show ECP status
            ecp = result['ecp_status']
            print(f"🧠 ECP: Stage {ecp['substrate']['stage']}, Paradoxes: {ecp['substrate']['paradox_count']}")
            
            # Show skill executions
            if result['skills_executed']:
                print("🛠️ Skills: {} executed".format(len(result['skills_executed'])))
                for skill in result['skills_executed']:
                    print(f"   - {skill['name']} (score: {skill['score']})")
            
            # Show context usage
            print(f"📊 Context: {result['context_used']:.0f} tokens")
            
        except Exception as e:
            logger.error(f"❌ Processing error: {e}")
            print(f"❌ Error: {e}")
    
    def show_help(self):
        """Show available commands"""
        print("\n📋 Vargas V4 Commands:")
        print("  message <text>        - Send message to Vargas")
        print("  status               - Show ECP and system status")
        print("  skills               - List available OpenClaw skills")
        print("  help                 - Show this help")
        print("  quit/exit/stop       - Stop the server")
        print("\n🎯 Examples:")
        print("  'message: Help me with hierarchical planning'")
        print("  'What about paradox processing?'")
        print("  'Show me emotional modulation'")
        print("  'Python programming assistance'")
    
    def show_status(self):
        """Show current system status"""
        print("\n📊 Vargas V4 Status:")
        
        # Get ECP status
        ecp_status = self.agent.get_ecp_status()
        
        print("🧠 ECP Architecture:")
        print(f"  Stage: {ecp_status['substrate']['stage']}")
        print(f"  Threshold: {ecp_status['substrate']['threshold']:.3f}")
        print(f"  Paradoxes: {ecp_status['substrate']['paradox_count']}")
        print(f"  Vector Magnitude: {ecp_status['substrate']['vector_magnitude']:.3f}")
        
        print("\n🔄 Forgetting Engine:")
        print(f"  Active Traces: {ecp_status['forgetting_engine']['active_traces']}")
        print(f"  Current Cycle: {ecp_status['forgetting_engine']['current_cycle']}")
        print(f"  Total Deleted: {ecp_status['forgetting_engine']['total_deleted']}")
        print(f"  Total Promoted: {ecp_status['forgetting_engine']['total_promoted']}")
        
        print("\n💾 Memory State:")
        print(f"  Context Tokens: {ecp_status['memory_state']['context_tokens']:.0f}")
        print(f"  Compression: {'Active' if ecp_status['memory_state']['compression_triggered'] else 'Inactive'}")
        print(f"  Conversation Length: {ecp_status['memory_state']['conversation_length']}")
        
        print(f"\n🛠️ OpenClaw:")
        print(f"  Available: {ecp_status['openclaw']['available']}")
        print(f"  Skills Available: {ecp_status['openclaw']['available_skills']}")
        print(f"  Skills Executed: {ecp_status['openclaw']['skills_executed']}")
        
        print(f"\n📝 Session:")
        print(f"  Session ID: {self.session_id}")
        print(f"  Messages Processed: {len(self.conversation_history)}")
        print(f"  Server Running: {self.is_running}")
    
    def show_skills(self):
        """Show available OpenClaw skills"""
        skills = self.agent.openclaw.get_available_skills()
        
        print(f"\n🛠️ Available OpenClaw Skills ({len(skills)}):")
        
        # Group by mode
        by_mode = {}
        for skill in skills:
            # Get skill details from manifest
            skill_name = skill
            # Try to get mode from agent's loaded skills
            mode = "unknown"
            
            # Check if this skill is in the agent's loaded skills
            matched = self.agent.openclaw.match_skills(skill_name, top_k=1)
            if matched:
                mode = matched[0].get('mode', 'unknown')
            
            if mode not in by_mode:
                by_mode[mode] = []
            by_mode[mode].append(skill_name)
        
        for mode, skill_list in by_mode.items():
            print(f"\n  {mode.upper()} ({len(skill_list)} skills):")
            for skill in skill_list[:10]:  # Show first 10 per mode
                print(f"    - {skill}")
            if len(skill_list) > 10:
                print(f"    ... and {len(skill_list) - 10} more")
    
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

async def main():
    """Main entry point"""
    print("🚀 Vargas V4 Server Launcher")
    print("🤖 Your Customized OpenClaw Agent")
    print("🧠 ECP Architecture + 99 Semantic Skills")
    print("=" * 60)
    
    # Create and start server
    server = VargasServer()
    await server.start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
