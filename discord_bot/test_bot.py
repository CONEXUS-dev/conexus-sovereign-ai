import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Test bot is online!")

@bot.command()
async def ping(ctx):
    print(f"Ping command received from {ctx.author}")
    await ctx.send("Pong!")

@bot.command()
async def hello(ctx):
    print(f"Hello command received from {ctx.author}")
    await ctx.send(f"Hello {ctx.author.mention}!")

# Run the bot
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN == "YOUR_TOKEN_HERE":
    print("ERROR: Please set DISCORD_TOKEN in .env file")
else:
    bot.run(DISCORD_TOKEN)
