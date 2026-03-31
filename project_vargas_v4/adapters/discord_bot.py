"""
VARGAS V4 Discord Adapter — Bridge to Discord API

This adapter connects the SovereignPerceptionLoop to Discord for real-time
interaction. It handles message routing, state management, and provides the
interface between Discord users and the VARGAS sovereign runtime.

Phase 7.3: Decoupled interface — conversational plain text by default,
State Embed on !cockpit command or automated forensic triggers
(RESOLUTION_GATE, Tier 3/4 approval).
"""

import os
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Add project root to Python path for imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.perception_loop import SovereignPerceptionLoop
from adapters.discord_ui import DiscordUI
from adapters.response_synthesizer import ResponseSynthesizer
from governance.boot_integrity import BootIntegrity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class VargasDiscordBot(commands.Bot):
    """
    Discord bot for VARGAS V4 sovereign runtime interaction.
    
    Default: conversational plain text via ResponseSynthesizer.
    State Embed on !cockpit command or automated forensic triggers.
    Boot integrity check on connect.
    """
    
    def __init__(self):
        # Initialize bot with required intents
        intents = discord.Intents.default()
        intents.message_content = True  # Required to read message content
        intents.guilds = True  # Required to access guild/channel info
        
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            help_command=None  # Disable default help command
        )
        
        # Configuration
        self.discord_token = os.getenv("DISCORD_TOKEN")
        self.allowed_channels = self._load_allowed_channels()
        
        # Initialize VARGAS components
        self.perception_loop = None
        self._initialize_perception_loop()
        
        # Initialize UI renderer (Phase 7.2 — Architect domain)
        self.discord_ui = DiscordUI()
        
        # Initialize response synthesizer (Phase 7.3 — Interface decoupling)
        self.response_synth = ResponseSynthesizer()
        
        # Per-channel last result cache for !cockpit command
        self._last_results: dict[int, dict] = {}
        
        # Register commands
        self._register_commands()
        
        logger.info("VARGAS Discord Bot initialized")
    
    def _register_commands(self):
        """Register bot commands."""
        
        @self.command(name="cockpit")
        async def cockpit(ctx: commands.Context):
            """On-demand State Embed — brings up the forensic dashboard."""
            if ctx.channel.id not in self.allowed_channels:
                return
            
            last_result = self._last_results.get(ctx.channel.id)
            
            if not last_result:
                await ctx.send("No state data yet. Send a message first.")
                return
            
            embed = self.discord_ui.build_state_embed(last_result)
            await ctx.send(embed=embed)
            logger.info(f"Cockpit embed requested by {ctx.author.name}")
        
        @self.command(name="status")
        async def status(ctx: commands.Context):
            """System status summary."""
            if ctx.channel.id not in self.allowed_channels:
                return
            
            if not self.perception_loop:
                await ctx.send("⚠️ VARGAS systems offline.")
                return
            
            sys_status = self.perception_loop.get_system_status()
            e_vec = sys_status.get("e_vector", {})
            trust = sys_status.get("trust_model", {})
            gate = sys_status.get("resolution_gate", {})
            safety = sys_status.get("safety", {})
            
            lines = [
                f"**Session**: `{sys_status.get('session_id', 'unknown')[:8]}` | **Boot**: {sys_status.get('boot_mode', 'UNKNOWN')}",
                f"**Uptime**: {sys_status.get('session_duration_minutes', 0)} min | **Turns**: {sys_status.get('turn_count', 0)}",
                f"**E-Vector**: 🌀 {e_vec.get('entropy', 0):.2f}  ⚖️ {e_vec.get('challenge_threshold', 0):.2f}  ⚡ {e_vec.get('initiative_threshold', 0):.2f}  🎯 {e_vec.get('directness_index', 0):.2f}",
                f"**Trust**: max_tier={trust.get('max_allowed_tier', '?')} | contradiction_escalation={trust.get('contradiction_escalation', False)}",
                f"**Resolution Gate**: {gate.get('state', 'OPEN')} | severity={gate.get('severity', 0.0):.2f}",
                f"**Qdrant**: {'connected' if sys_status.get('memory_status', {}).get('qdrant_available') else 'fallback'}",
                f"**Provenance**: {sys_status.get('provenance', {}).get('entries_logged', 0)} chain | {sys_status.get('provenance', {}).get('action_log_entries', 0)} actions",
                f"**Safety**: {safety.get('rollback_snapshots', 0)} snapshots | {safety.get('forbidden_ops_blocked', 0)} blocked",
            ]
            await ctx.send("\n".join(lines))
            logger.info(f"Status requested by {ctx.author.name}")
    
    def _load_allowed_channels(self) -> list[int]:
        """Load allowed channel IDs from environment or use defaults."""
        channels_str = os.getenv("ALLOWED_CHANNELS", "")
        if channels_str:
            try:
                return [int(channel_id.strip()) for channel_id in channels_str.split(",")]
            except ValueError:
                logger.warning("Invalid ALLOWED_CHANNELS format, using empty list")
                return []
        
        # Default to empty list (no channels allowed) for security
        logger.info("No ALLOWED_CHANNELS configured, bot will not respond to messages")
        return []
    
    def _initialize_perception_loop(self):
        """Initialize the SovereignPerceptionLoop with boot integrity check."""
        try:
            # Run boot integrity check FIRST — constitution before runtime
            self.boot_integrity = BootIntegrity(str(project_root))
            boot_mode = self.boot_integrity.boot_mode
            logger.info(f"Boot integrity check: mode={boot_mode}")
            
            config_path = project_root / "config" / "sovereign_state.json"
            self.perception_loop = SovereignPerceptionLoop(str(config_path))
            
            # Propagate boot mode to state controller and trust model
            self.perception_loop.state_controller.set_boot_mode(boot_mode)
            max_tier = self.boot_integrity.get_allowed_tiers()
            max_tier_num = max(int(t.split("_")[1]) for t in max_tier) if max_tier else 0
            self.perception_loop.trust_model.set_max_tier(max_tier_num)
            self.perception_loop.tool_executor.max_allowed_tier = max_tier_num
            
            # Log boot integrity to integrity log
            self.perception_loop.integrity_log.log_boot_check(
                boot_mode=boot_mode,
                constitution_hash=self.boot_integrity.verifier.canonical_hash or "",
                checks=self.boot_integrity.boot_report.get("checks", {}),
                session_id=self.perception_loop.session_id,
            )
            
            logger.info(f"SovereignPerceptionLoop initialized: boot_mode={boot_mode} max_tier={max_tier_num}")
        except Exception as e:
            logger.error(f"Failed to initialize SovereignPerceptionLoop: {e}")
            self.perception_loop = None
            self.boot_integrity = None
    
    async def on_ready(self):
        """Called when the bot successfully connects to Discord."""
        logger.info(f"VARGAS V4 bot is online: {self.user.name} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Log allowed channels
        if self.allowed_channels:
            logger.info(f"Allowed channels: {self.allowed_channels}")
            for channel_id in self.allowed_channels:
                try:
                    channel = self.get_channel(channel_id)
                    if channel:
                        logger.info(f"  - #{channel.name} in {channel.guild.name}")
                    else:
                        logger.warning(f"  - Channel {channel_id} not found")
                except Exception as e:
                    logger.warning(f"  - Error accessing channel {channel_id}: {e}")
        else:
            logger.warning("No allowed channels configured - bot will not respond")
        
        # Boot integrity check — send provenance chain verification to first allowed channel
        await self._run_boot_integrity_check()
    
    async def _run_boot_integrity_check(self):
        """Run provenance chain verification on boot and send result to Discord.
        
        Sends raw hash verification data — no narrative, no interpretation.
        """
        if not self.perception_loop or not self.allowed_channels:
            return
        
        try:
            verification = self.perception_loop.provenance_logger.verify_chain()
            session_id = self.perception_loop.session_id
            embed = self.discord_ui.build_integrity_embed(verification, session_id)
            
            # Send to first allowed channel
            channel = self.get_channel(self.allowed_channels[0])
            if channel:
                await channel.send(embed=embed)
                logger.info(
                    "Boot integrity check sent: valid=%s entries=%d",
                    verification.get("valid"), verification.get("entries_checked"),
                )
        except Exception as e:
            logger.error(f"Boot integrity check failed: {e}")
    
    async def on_message(self, message: discord.Message):
        """Called when a message is sent in any channel the bot can see.
        
        Default: plain text reply via ResponseSynthesizer.
        Auto-embed: RESOLUTION_GATE active or Tier 3/4 action pending.
        On-demand: !cockpit command (handled separately).
        """
        
        # Ignore messages from bots (including ourselves)
        if message.author.bot:
            return
        
        # Only respond in allowed channels
        if message.channel.id not in self.allowed_channels:
            return
        
        # Let commands process first (!cockpit, etc.)
        await self.process_commands(message)
        
        # If the message is a command, don't also process it as a regular message
        ctx = await self.get_context(message)
        if ctx.valid:
            return
        
        # Log the incoming message
        logger.info(f"Message from {message.author.name} in #{message.channel.name}: {message.content[:100]}...")
        
        # Check if Perception Loop is available
        if not self.perception_loop:
            await message.channel.send("⚠️ VARGAS systems offline. Please try again later.")
            return
        
        try:
            # Indicate processing
            async with message.channel.typing():
                # Process message through SovereignPerceptionLoop
                result = self.perception_loop.process_message(message.content)
                
                # Cache result for !cockpit retrieval
                self._last_results[message.channel.id] = result
                
                # Default: send plain text via ResponseSynthesizer
                verbal_reply = self.response_synth.synthesize(result)
                
                # Append approval notice if Tier 3/4 action pending
                action_result = result.get("action_result")
                if action_result:
                    verbal_reply += self.response_synth.format_approval_notice(action_result)
                
                await message.channel.send(verbal_reply)
                
                # Automated forensic trigger: send State Embed if conditions met
                if self.response_synth.should_auto_embed(result):
                    embed = self.discord_ui.build_state_embed(result)
                    await message.channel.send(embed=embed)
                    logger.info(
                        f"Auto-embed sent to {message.author.name}: "
                        f"state={result.get('contradiction_info', {}).get('state')}"
                    )
                
                # Log the interaction
                state = result.get("contradiction_info", {}).get("state", "WITNESS_MODE")
                logger.info(f"Reply sent to {message.author.name}: state={state}")
        
        except Exception as e:
            logger.error(f"Error processing message from {message.author.name}: {e}")
            await message.channel.send("❌ Error processing your message. Please try again.")
    
    async def close(self):
        """Clean shutdown of the bot and its components."""
        logger.info("Shutting down VARGAS Discord Bot...")
        
        # Close Perception Loop if initialized
        if self.perception_loop:
            try:
                # Get final system status for logging
                status = self.perception_loop.get_system_status()
                logger.info(f"Final session stats: {status.get('session_id', 'unknown')}")
            except Exception as e:
                logger.warning(f"Error getting final status: {e}")
        
        # Close Discord connection
        await super().close()
        logger.info("VARGAS Discord Bot shutdown complete")


def main():
    """Main entry point for the Discord bot."""
    # Check for Discord token
    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        logger.error("DISCORD_TOKEN not found in environment variables")
        logger.error("Please set DISCORD_TOKEN in your .env file")
        return
    
    # Check for allowed channels
    allowed_channels = os.getenv("ALLOWED_CHANNELS")
    if not allowed_channels:
        logger.warning("ALLOWED_CHANNELS not configured")
        logger.warning("Bot will connect but will not respond to any messages")
        logger.warning("Set ALLOWED_CHANNELS in your .env file (comma-separated channel IDs)")
    
    # Create and run bot
    bot = VargasDiscordBot()
    
    try:
        logger.info("Starting VARGAS V4 Discord Bot...")
        bot.run(discord_token)
    except discord.errors.LoginFailure:
        logger.error("Invalid Discord token - please check DISCORD_TOKEN")
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    main()
