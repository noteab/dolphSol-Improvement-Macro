import discord
from discord import commands
import os
import json

base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, 'data', 'settings', 'config.json')

try:
    with open(config_path, 'r') as file:
        config_data = json.load(file)
        bot_token = config_data.get("bot_token")
except FileNotFoundError:
    print(f"File not found: {config_path}")
    raise

intents = discord.Intents.default()
latest_biome = 'sandstorm'
latest_merchant = 'mari'

bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.slash_command(name="current_biome", description="Notifies the user with the current biome")
async def current_biome(ctx):
    await ctx.respond(f"The current biome is {latest_biome}")

@bot.slash_command(name="last_merchant", description="Name of the last merchant that spawned")
async def last_merchant(ctx):
    await ctx.respond(f"The last merchant that spawned is {latest_merchant}")

@bot.slash_command(name="click_specific_position", description="Clicks the specified position")
async def click_specific_position(ctx, position_input: str):
    global click_specific_position
    click_specific_position = position_input
    await ctx.respond("The position has been clicked")

bot.run(bot_token)
