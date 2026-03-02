import discord
from discord.ext import commands
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# CONEXUS Gateway Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://127.0.0.1:18789")
GATEWAY_HEALTH_ENDPOINT = f"{GATEWAY_URL}/health"
GATEWAY_TASK_ENDPOINT = f"{GATEWAY_URL}/tasks"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("CONEXUS Discord Bot is online!")
    # Check Gateway connection
    try:
        response = requests.get(GATEWAY_HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            print("✅ Connected to CONEXUS Gateway")
        else:
            print("⚠️ Gateway connection issues")
    except Exception as e:
        print(f"❌ Cannot connect to Gateway: {e}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def status(ctx):
    """Check CONEXUS system status"""
    try:
        # Check Gateway health
        gateway_response = requests.get(GATEWAY_HEALTH_ENDPOINT, timeout=5)
        
        if gateway_response.status_code == 200:
            gateway_data = gateway_response.json()
            
            # Check Qdrant status
            qdrant_response = requests.get("http://localhost:6333/collections/conexus_lineage", timeout=5)
            qdrant_data = qdrant_response.json()
            
            embed = discord.Embed(
                title="🤖 CONEXUS System Status",
                color=discord.Color.green()
            )
            embed.add_field(name="Gateway", value=f"✅ Online (v{gateway_data.get('version', 'Unknown')})", inline=False)
            embed.add_field(name="Memory Vectors", value=f"📊 {qdrant_data['result']['points_count']} stored", inline=False)
            embed.add_field(name="System", value="🟢 Operational", inline=False)
            embed.set_footer(text="Sovereign AI System - Human Directed")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Gateway is not responding")
            
    except Exception as e:
        await ctx.send(f"❌ Error checking status: {str(e)}")

@bot.command()
async def outer(ctx, *, query: str = None):
    """Direct query to the calibrated Outer Agent (Phi-4-mini)"""
    if not query:
        await ctx.send("Usage: `!outer <query>`")
        return
    await _submit_task(ctx, query, agent_assignment="outer")


@bot.command()
async def conexus(ctx, *, query: str = None):
    """Main CONEXUS sovereign AI interaction (smart-routed)"""
    if not query:
        await ctx.send("Please provide a query for CONEXUS. Example: `!conexus analyze the AI market opportunity`")
        return
    await _submit_task(ctx, query, agent_assignment="auto")


@bot.command()
async def opie(ctx, *, query: str = None):
    """Invoke Opie (Become Agent) directly for creative synthesis"""
    if not query:
        await ctx.send("Please provide a query for Opie. Example: `!opie what identity shift is emerging?`")
        return
    await _submit_task(ctx, query, agent_assignment="opie")


@bot.command()
async def synthesize(ctx, *, query: str = None):
    """Creative synthesis using Opie's Become-mode capabilities"""
    if not query:
        await ctx.send("Please provide a topic to synthesize. Example: `!synthesize sovereign AI and human creativity`")
        return
    await _submit_task(ctx, f"synthesize and expand: {query}", agent_assignment="opie")


@bot.command()
async def become(ctx, *, query: str = None):
    """Become-mode identity expansion using both agents"""
    if not query:
        await ctx.send("Please provide context for Become processing. Example: `!become what is CC evolving into?`")
        return
    await _submit_task(ctx, query, agent_assignment="both")


async def _submit_task(ctx, query: str, agent_assignment: str = "auto"):
    """Submit a task to the Gateway and format the response"""
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

        response = requests.post(GATEWAY_TASK_ENDPOINT, json=task_data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            agent = result.get("agent", "sway")
            embed = _format_response(query, result, agent)
            await ctx.send(embed=embed)

            # If Opie flagged handoff items, notify
            handoff = result.get("handoff_to_sway", [])
            if handoff:
                handoff_text = "\n".join(f"• {h.get('signal', 'unknown')}" for h in handoff[:5])
                handoff_embed = discord.Embed(
                    title="🔄 Handoff to Sway",
                    description=f"Opie identified items requiring execution:\n{handoff_text}",
                    color=discord.Color.orange()
                )
                handoff_embed.set_footer(text="Use !conexus or !analyze to have Sway execute these")
                await ctx.send(embed=handoff_embed)
        else:
            await ctx.send(f"❌ Gateway error: {response.status_code}")

    except Exception as e:
        await ctx.send(f"❌ Error processing request: {str(e)}")


def _format_response(query: str, result: dict, agent: str) -> discord.Embed:
    """Format a Gateway response as a Discord embed"""
    # Agent-specific colors and icons
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

    status = result.get("status", "unknown")
    if status == "ok":
        output = result.get("task_output", "Processing complete")
        # Truncate for Discord embed limits (1024 chars per field)
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
                value=f"{routing.get('routing_method', 'unknown')} → {routing.get('routed_to', 'unknown')}",
                inline=True
            )

        # Proto-moments (Opie-specific)
        proto = result.get("proto_moments", [])
        if proto:
            proto_text = "\n".join(f"• {m[:150]}" for m in proto[:3])
            embed.add_field(name="✨ Proto-Moments", value=proto_text, inline=False)

        embed.set_footer(text="Sovereign AI — Human Directed")
    else:
        embed.add_field(name="❌ Error", value=result.get("error", "Unknown error"), inline=False)
        embed.color = discord.Color.red()

    return embed

@bot.command()
async def sway(ctx, *, query: str = None):
    """Invoke Sway (Collapse Agent) directly for analysis and execution"""
    if not query:
        await ctx.send("Please provide a query for Sway. Example: `!sway analyze the technical architecture`")
        return
    await _submit_task(ctx, query, agent_assignment="sway")


@bot.command()
async def analyze(ctx, *, topic: str = None):
    """Strategic analysis using Sway (Collapse Agent)"""
    if not topic:
        await ctx.send("Please provide a topic for analysis. Example: `!analyze sovereign AI market opportunity`")
        return
    await _submit_task(ctx, f"strategic analysis of {topic}", agent_assignment="sway")


@bot.command()
async def narrative(ctx, *, topic: str = None):
    """Create narrative using Opie's Become-mode storytelling"""
    if not topic:
        await ctx.send("Please provide a topic for narrative creation. Example: `!narrative the future of sovereign AI`")
        return
    await _submit_task(ctx, f"create strategic narrative about {topic}", agent_assignment="opie")

@bot.command()
async def help_conexus(ctx):
    """CONEXUS command help"""
    embed = discord.Embed(
        title="🤖 CONEXUS Discord Commands",
        description="Interact with the CONEXUS sovereign AI system",
        color=discord.Color.purple()
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
            "`!conexus <query>` — Smart-routed interaction\n"
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
            "`!become <query>` — Full Collapse+Become processing\n"
        ),
        inline=False
    )
    embed.add_field(
        name="🔧 System",
        value=(
            "`!status` — System health check\n"
            "`!help_conexus` — This help message\n"
        ),
        inline=False
    )

    embed.set_footer(text="CONEXUS — Sovereign AI · Human Directed")
    await ctx.send(embed=embed)

# Run the bot
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_TOKEN_HERE")
bot.run(DISCORD_TOKEN)
