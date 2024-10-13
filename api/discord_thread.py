import asyncio
import os
import aiohttp
import discord
import requests
import uvicorn
from pipeline.db import AgentStateManager
from models import Message

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if (
        (message.channel.id not in [1294545886281469972])
        and message.channel.parent
        and message.channel.parent.id not in [1294545886281469972]
    ):
        return

    if isinstance(message.channel, discord.Thread):
        thread = message.channel
        print(thread.name)
        # Get the entire conversation history of the thread
        messages = []
        async for msg in thread.history(limit=None):
            messages.append(
                Message(
                    user_id=str(msg.author.id),
                    message=msg.content,
                    name="assistant"
                    if msg.author.id == 1294750513795174450
                    else msg.author.name,
                ).model_dump()
            )

        # Reverse the list to get messages in chronological order
        messages.reverse()

        print(f"Retrieved {len(messages)} messages from the thread.")

        # Now you can use these messages to send to your API
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(
        #         f"{os.getenv('API_URL', 'http://localhost:8080')}/agent",
        #         json=messages
        #     ) as response:
        #         agent_response = await response.json()
        # await thread.send(f"Processing your request. Agent ID: {agent_id}")
        # requests.post(
        #     f"{os.getenv('API_URL', 'http://localhost:8080')}/agent",  # noqa: F821
        #     json=[Message("user_id": "discord_bot", "message": message.content) for message in thread]
        # )
    else:
        # Create a new thread for the question
        print(message.content)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{os.getenv('API_URL', 'http://localhost:8080')}/agent",
                json=[
                    Message(
                        user_id=str(message.author.id),
                        message=message.content,
                        avatar_url=message.author.display_avatar.url,
                    ).model_dump()
                ],
            ) as response:
                agent_response = await response.json()

        if "id" not in agent_response:
            print(agent_response)
            return
        print(agent_response)
        agent_id = agent_response["id"]
        thread = await message.create_thread(
            name=agent_response["title"]
        )
        await thread.send("working on it...")

        async with thread.typing():
            while True:
                state = AgentStateManager.from_id(agent_id)
                final = state.final_state()
                if final is not None:
                    await thread.send(final)
                    return
                else:
                    await asyncio.sleep(1)


async def run_bot():
    try:
        await client.start(os.getenv("DISCORD_BOT_TOKEN") or "")  # noqa: F821
    except KeyboardInterrupt:
        print("Shutting down bot...")
        await client.close()
    except Exception as e:
        print("An error occurred while running the bot.")
    
