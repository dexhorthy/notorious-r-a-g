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
        message_data =  {
                "author": message.author.name,
                "content": message.content,
                "timestamp": str(message.created_at),
                "id": message.id,
                "parent_id": None,
                "thread_id": None
            }
        if message.reference:
            # The reference attribute contains information about the message being replied to
            message_data["parent_id"] = message.reference.message_id
        
        if message.thread:
            message_data["thread_id"] = message.thread.id
        messages.append(message_data)
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
