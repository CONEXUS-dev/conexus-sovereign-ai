"""
Sovereign Bot — CONEXUS Discord Presence
Standalone Discord bot with optional Gateway integration.
"""

import discord
from discord.ext import commands
import aiohttp
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot setup with required intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

# Gateway configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8002")


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"✅ Connected to {len(bot.guilds)} server(s):")
    for guild in bot.guilds:
        print(f"   - {guild.name} ({guild.member_count} members)")
    # Check Gateway
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GATEWAY_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    print(f"✅ Gateway connected at {GATEWAY_URL}")
                else:
                    print(f"⚠️ Gateway responded with {resp.status}")
    except Exception:
        print(f"⚠️ Gateway not reachable at {GATEWAY_URL} — bot works, agent commands won't")
    print("✅ Sovereign is online.")


# ---------------------------------------------------------------------------
# Basic Commands
# ---------------------------------------------------------------------------

@bot.event
async def on_message(message):
    """Debug: log every message the bot sees"""
    if message.author == bot.user:
        return
    print(f"[MSG] #{message.channel.name} | {message.author}: {message.content}")
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    """Log command errors"""
    print(f"[ERR] Command error: {error}")


@bot.command()
async def ping(ctx):
    """Check if Sovereign is alive"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! ({latency}ms)")


@bot.command()
async def hello(ctx):
    """Greet the user"""
    await ctx.send(f"Hello {ctx.author.mention}. I'm Sovereign — the CONEXUS system interface.")


@bot.command()
async def info(ctx):
    """Show system info"""
    embed = discord.Embed(
        title="Sovereign — CONEXUS System",
        description="Sovereign multi-agent AI system. Human-directed. Always.",
        color=discord.Color.purple()
    )
    embed.add_field(name="Agents", value="**Outer** (Phi-4-mini) · **Sway** (Collapse) · **Opie** (Become)", inline=False)
    embed.add_field(name="Protocol", value="Collapse–Become Unified Protocol v1.1", inline=False)
    embed.add_field(name="Orchestrator", value="Derek (Principal Orchestrator)", inline=False)
    embed.add_field(
        name="Status",
        value=f"Online since {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        inline=False
    )
    embed.set_footer(text="CONEXUS — Sovereign AI · Human Directed")
    await ctx.send(embed=embed)


@bot.command()
async def status(ctx):
    """Check full system status (Gateway + Qdrant)"""
    embed = discord.Embed(
        title="🤖 CONEXUS System Status",
        color=discord.Color.green()
    )
    # Gateway
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GATEWAY_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed.add_field(name="Gateway", value=f"✅ Online (v{data.get('version', '?')})", inline=False)
                else:
                    embed.add_field(name="Gateway", value="⚠️ Responding with errors", inline=False)
    except Exception:
        embed.add_field(name="Gateway", value="❌ Offline", inline=False)
        embed.color = discord.Color.orange()
    # Qdrant
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:6333/collections/conexus_lineage", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    points = data["result"]["points_count"]
                    embed.add_field(name="Memory (Qdrant)", value=f"✅ Online ({points} vectors)", inline=False)
                else:
                    embed.add_field(name="Memory (Qdrant)", value="⚠️ Responding with errors", inline=False)
    except Exception:
        embed.add_field(name="Memory (Qdrant)", value="❌ Offline", inline=False)
    embed.set_footer(text="Sovereign AI — Human Directed")
    await ctx.send(embed=embed)


# ---------------------------------------------------------------------------
# Agent Commands (require Gateway)
# ---------------------------------------------------------------------------

async def _gateway_task(ctx, query: str, agent_assignment: str):
    """Submit a task to the Gateway and display the response."""
    try:
        task_data = {
            "task_input": query,
            "agent_assignment": agent_assignment,
            "security_context": {
                "user_id": str(ctx.author.id),
                "channel_id": str(ctx.channel.id),
                "timestamp": datetime.now().isoformat()
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{GATEWAY_URL}/tasks",
                json=task_data,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    agent = result.get("agent", "sway")
                    embed = _format_response(query, result, agent)
                    await ctx.send(embed=embed)
                    # Handoff notifications
                    handoff = result.get("handoff_to_sway", [])
                    if handoff:
                        handoff_text = "\n".join(f"• {h.get('signal', 'unknown')}" for h in handoff[:5])
                        h_embed = discord.Embed(
                            title="🔄 Handoff to Sway",
                            description=f"Opie identified items requiring execution:\n{handoff_text}",
                            color=discord.Color.orange()
                        )
                        h_embed.set_footer(text="Use !analyze or !sway to have Sway execute these")
                        await ctx.send(embed=h_embed)
                else:
                    await ctx.send(f"❌ Gateway error: {resp.status}")
    except aiohttp.ClientError:
        await ctx.send(f"❌ Cannot reach Gateway at {GATEWAY_URL}. Is it running?")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)[:200]}")


def _format_response(query: str, result: dict, agent: str) -> discord.Embed:
    """Format a Gateway response as a Discord embed."""
    agent_config = {
        "outer": {"color": discord.Color.green(), "icon": "🧠", "label": "Outer (Phi-4-mini)"},
        "sway": {"color": discord.Color.blue(), "icon": "⚡", "label": "Sway (Collapse)"},
        "opie": {"color": discord.Color.purple(), "icon": "🌀", "label": "Opie (Become)"},
        "both": {"color": discord.Color.gold(), "icon": "🔄", "label": "Sway + Opie"},
    }
    config = agent_config.get(agent, agent_config["sway"])
    embed = discord.Embed(
        title=f"{config['icon']} CONEXUS Response",
        description=f"**Query:** {query[:200]}",
        color=config["color"]
    )
    status_val = result.get("status", "unknown")
    if status_val == "ok" or status_val == "accepted":
        output = result.get("task_output", "Processing complete")
        if len(output) > 1000:
            output = output[:997] + "..."
        embed.add_field(name="📋 Response", value=output, inline=False)
        embed.add_field(name="🤖 Agent", value=config["label"], inline=True)
        gear = result.get("gear_context") or result.get("gear", "")
        if gear:
            embed.add_field(name="⚙️ Gear", value=gear, inline=True)
        routing = result.get("routing", {})
        if routing:
            embed.add_field(
                name="🔀 Routing",
                value=f"{routing.get('routing_method', '?')} → {routing.get('routed_to', '?')}",
                inline=True
            )
        proto = result.get("proto_moments", [])
        if proto:
            proto_text = "\n".join(f"• {m[:150]}" for m in proto[:3])
            embed.add_field(name="✨ Proto-Moments", value=proto_text, inline=False)
    else:
        embed.add_field(name="❌ Error", value=result.get("error", "Unknown error"), inline=False)
        embed.color = discord.Color.red()
    embed.set_footer(text="Sovereign AI — Human Directed")
    return embed


@bot.command()
async def outer(ctx, *, query: str = None):
    """Direct query to the calibrated Outer Agent (Phi-4-mini)"""
    if not query:
        await ctx.send("Usage: `!outer <query>`")
        return
    await _gateway_task(ctx, query, agent_assignment="outer")


@bot.command()
async def conexus(ctx, *, query: str = None):
    """Smart-routed CONEXUS query"""
    if not query:
        await ctx.send("Usage: `!conexus <query>`")
        return
    await _gateway_task(ctx, query, agent_assignment="auto")


@bot.command(name="sway")
async def sway_cmd(ctx, *, query: str = None):
    """Direct query to Sway (Collapse Agent)"""
    if not query:
        await ctx.send("Usage: `!sway <query>`")
        return
    await _gateway_task(ctx, query, agent_assignment="sway")


@bot.command(name="opie")
async def opie_cmd(ctx, *, query: str = None):
    """Direct query to Opie (Become Agent)"""
    if not query:
        await ctx.send("Usage: `!opie <query>`")
        return
    await _gateway_task(ctx, query, agent_assignment="opie")


@bot.command()
async def synthesize(ctx, *, query: str = None):
    """Creative synthesis via Opie"""
    if not query:
        await ctx.send("Usage: `!synthesize <topic>`")
        return
    await _gateway_task(ctx, f"synthesize and expand: {query}", agent_assignment="opie")


@bot.command()
async def become(ctx, *, query: str = None):
    """Full Collapse+Become processing (both agents)"""
    if not query:
        await ctx.send("Usage: `!become <query>`")
        return
    await _gateway_task(ctx, query, agent_assignment="both")


@bot.command()
async def analyze(ctx, *, topic: str = None):
    """Strategic analysis via Sway"""
    if not topic:
        await ctx.send("Usage: `!analyze <topic>`")
        return
    await _gateway_task(ctx, f"strategic analysis of {topic}", agent_assignment="sway")


@bot.command()
async def narrative(ctx, *, topic: str = None):
    """Narrative creation via Opie"""
    if not topic:
        await ctx.send("Usage: `!narrative <topic>`")
        return
    await _gateway_task(ctx, f"create strategic narrative about {topic}", agent_assignment="opie")


@bot.command(name="help_sovereign")
async def help_sovereign(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="Sovereign Commands",
        description="Available commands for the CONEXUS system.",
        color=discord.Color.purple()
    )
    embed.add_field(
        name="General",
        value=(
            "`!ping` — Check bot latency\n"
            "`!hello` — Greet Sovereign\n"
            "`!info` — System information\n"
            "`!status` — Full system health check\n"
            "`!help_sovereign` — This message\n"
        ),
        inline=False
    )
    embed.add_field(
        name="🧠 Outer Agent (Phi-4-mini)",
        value=(
            "`!outer <query>` — Direct query to calibrated Outer Agent\n"
        ),
        inline=False
    )
    embed.add_field(
        name="⚡ Sway (Collapse Agent)",
        value=(
            "`!sway <query>` — Direct Collapse-mode query\n"
            "`!analyze <topic>` — Strategic analysis\n"
        ),
        inline=False
    )
    embed.add_field(
        name="🌀 Opie (Become Agent)",
        value=(
            "`!opie <query>` — Direct Become-mode query\n"
            "`!synthesize <topic>` — Creative synthesis\n"
            "`!narrative <topic>` — Strategic storytelling\n"
        ),
        inline=False
    )
    embed.add_field(
        name="🔄 Both Agents",
        value=(
            "`!conexus <query>` — Smart-routed query\n"
            "`!become <query>` — Full Collapse+Become\n"
        ),
        inline=False
    )
    embed.set_footer(text="CONEXUS — Sovereign AI · Human Directed")
    await ctx.send(embed=embed)


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not DISCORD_TOKEN or DISCORD_TOKEN.startswith("YOUR"):
    print("❌ DISCORD_TOKEN not set in .env file")
    print("   Edit discord_bot/.env and add your token.")
else:
    bot.run(DISCORD_TOKEN)
