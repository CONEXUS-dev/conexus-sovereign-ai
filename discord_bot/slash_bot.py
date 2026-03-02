import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

intents = discord.Intents.default()
# Note: Not requiring message_content intent - using slash commands instead

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Sovereign bot is online!")
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="ping")
async def slash_ping(interaction: discord.Interaction):
    """Simple ping command"""
    print(f"Ping command from {interaction.user}")
    await interaction.response.send_message("Pong!")

@bot.tree.command(name="hello")
async def slash_hello(interaction: discord.Interaction):
    """Say hello to Sovereign"""
    print(f"Hello command from {interaction.user}")
    await interaction.response.send_message(f"Hello {interaction.user.mention}! I'm Sovereign, your AI assistant.")

@bot.tree.command(name="sway")
async def slash_sway(interaction: discord.Interaction, query: str):
    """Ask Sway (Collapse Agent) for analysis"""
    print(f"Sway command from {interaction.user}: {query}")
    await interaction.response.send_message(f"Sway analysis request: {query}\n\n(Gateway integration coming soon!)")

@bot.tree.command(name="opie")
async def slash_opie(interaction: discord.Interaction, query: str):
    """Ask Opie (Become Agent) for synthesis"""
    print(f"Opie command from {interaction.user}: {query}")
    await interaction.response.send_message(f"Opie synthesis request: {query}\n\n(Gateway integration coming soon!)")

# Run the bot
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN == "YOUR_NEW_SOVEREIGN_TOKEN_HERE":
    print("ERROR: Please set DISCORD_TOKEN in .env file")
else:
    bot.run(DISCORD_TOKEN)
