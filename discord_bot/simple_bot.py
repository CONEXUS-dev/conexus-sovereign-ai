import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Minimal intents - no message content needed
intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Simple bot is online!")

@bot.event
async def on_message(message):
    # Don't respond to self
    if message.author == bot.user:
        return
    
    # Simple response to specific messages
    if message.content.lower() == "hello sovereign":
        print(f"Received: {message.content} from {message.author}")
        await message.channel.send(f"Hello {message.author.mention}!")
    
    # Process commands
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    print(f"Ping command from {ctx.author}")
    await ctx.send("Pong!")

# Run the bot
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN or DISCORD_TOKEN == "YOUR_NEW_SOVEREIGN_TOKEN_HERE":
    print("ERROR: Please set DISCORD_TOKEN in .env file")
else:
    bot.run(DISCORD_TOKEN)
