# Script to dump all messages of a discord channel to `channel_messages.json`

import discord
import json
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "FAKE_TOKEN")
CHANNEL_ID = 1253172394345107466  # Questions channel on BAML

client = discord.Client(intents=discord.Intents.default())


async def fetch_messages(channel):
    messages = []
    limit = None  # Fetches all messages in the channel
    async for message in channel.history(limit=limit):
        messages.append(
            {
                "author": message.author.name,
                "content": message.content,
                "timestamp": str(message.created_at),
                "id": message.id,
            }
        )
    return messages


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        messages = await fetch_messages(channel)
        with open("channel_messages.json", "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)
        print(f"Saved {len(messages)} messages to channel_messages.json")
    await client.close()


client.run(TOKEN)
