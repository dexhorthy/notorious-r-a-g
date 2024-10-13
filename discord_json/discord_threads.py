import discord
import json
import os
from dotenv import load_dotenv
from collections import defaultdict
load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "FAKE_TOKEN")
CHANNEL_ID = 1253172394345107466  # Questions channel on BAML

client = discord.Client(intents=discord.Intents.default())

async def fetch_messages(channel):
    messages = []
    limit = None  # Fetches all messages in the channel
    
    async for message in channel.history(limit=limit):
        message_data = await process_message(message)
        messages.append(message_data)
        
        # If the message starts a thread, fetch all messages in that thread
        if message.thread:
            thread = message.thread
            async for thread_message in thread.history(limit=None):
                thread_message_data = await process_message(thread_message, thread_id=thread.id, thread_name=thread.name)
                messages.append(thread_message_data)
        messages.sort(key=lambda x: x["timestamp"])
    organized_messages = defaultdict(list)
    for msg in messages:
        thread_id = msg["thread_id"]
        organized_messages[thread_id].append({
            "author": msg["author"],
            "timestamp": msg["timestamp"],
            "content": msg["content"],
            "thread_name": msg["thread_name"],
        })

    messages = [{"id": thread_id, "thread_name": msgs[1].get("thread_name"), "values": msgs} for thread_id, msgs in organized_messages.items()]
    for msg in messages:
        msg["values"] = list(map(lambda x: {k: v for k, v in x.items() if k != "thread_name"}, msg["values"]))

    return messages


async def process_message(message, thread_id=None, thread_name=None):
    message_data = {
        "author": message.author.name,
        "content": message.content,
        "timestamp": str(message.created_at),
        "id": message.id,
        "parent_id": None,  # Default to None if it's not a reply
        "thread_id": thread_id,  # Will be None for channel messages, set for thread messages
        "thread_name": thread_name
    }
    
    # Check if the message is a reply
    if message.reference:
        # The reference attribute contains information about the message being replied to
        message_data["parent_id"] = message.reference.message_id
    
    # If it's a channel message that starts a thread, set the thread_id
    if not thread_id and message.thread:
        message_data["thread_id"] = message.thread.id
    
    return message_data

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        messages = await fetch_messages(channel)
        with open("thread_messages.json", "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)
        print(f"Saved {len(messages)} messages to thread_messages.json")
    await client.close()


client.run(TOKEN)
