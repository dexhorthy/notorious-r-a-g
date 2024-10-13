import os
import aiohttp
import discord
import requests
from dotenv import load_dotenv
from models import Message

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if (
        message.channel.id not in [1294545886281469972]
    ) and message.channel.parent.id not in [1294545886281469972]:
        return

    if not message.content.startswith("$help"):
        return

    if isinstance(message.channel, discord.Thread):
        thread = message.channel
        print(thread.name)
        # Get the entire conversation history of the thread
        messages = []
        async for msg in thread.history(limit=None):
            messages.append(Message(
                user_id=str(msg.author.id),
                message=msg.content,
                name="assistant" if msg.author.id == 1294750513795174450 else msg.author.name
            ).model_dump())
        
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

        agent_id = agent_response["id"]
        # await thread.send(f"Processing your request. Agent ID: {agent_id}")
        # requests.post(
        #     f"{os.getenv('API_URL', 'http://localhost:8080')}/agent",  # noqa: F821
        #     json=[Message("user_id": "discord_bot", "message": message.content) for message in thread]
        # )
    else:
        # Create a new thread for the question
        thread = await message.create_thread(
            name="New Question Thread", auto_archive_duration=60
        )

        await thread.send("working on it...")

        print(message.content)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{os.getenv('API_URL', 'http://localhost:8080')}/agent",
                json=[
                    Message(
                        user_id=str(message.author.id), message=message.content
                    ).model_dump()
                ],
            ) as response:
                agent_response = await response.json()

        agent_id = agent_response["id"]

        await thread.typing()
        while True:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{os.getenv('API_URL', 'http://localhost:8080')}/agent/{agent_id}"  # noqa: F821
                ) as response:
                    final_state = await response.json()
            if final_state is None:
                continue
            await thread.send(final_state)
            break


if __name__ == "__main__":
    client.run(os.getenv("DISCORD_BOT_TOKEN") or "")  # noqa: F821
