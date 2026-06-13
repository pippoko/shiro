import discord
from discord import app_commands
from discord.ext import commands
import requests
import os

TOKEN = os.getenv("DISCORD_TOKEN")
GAS_URL = os.getenv("GAS_URL")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

@bot.event
async def on_ready():
    print("Bot is ready")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.tree.command(name="random")
async def random_info(interaction: discord.Interaction):
    res = requests.post(GAS_URL, json={"command": "random"})
    data = res.json()
    await interaction.response.send_message(data["result"])

bot.run(TOKEN)
