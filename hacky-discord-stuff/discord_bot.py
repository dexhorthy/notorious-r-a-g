import os
import discord
from discord.ext import commands
from llama_index.readers.discord import DiscordReader


discord_token = os.getenv("DISCORD_BOT_TOKEN")
channel_ids = [1272969803921096779]  # Replace with your channel_id
reader = DiscordReader(discord_token=discord_token)
documents = reader.load_data(channel_ids=channel_ids)