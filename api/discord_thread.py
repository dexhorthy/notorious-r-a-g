import os
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
        resp = requests.post(
            f"{os.getenv('API_URL', 'http://localhost:8080')}/agent",  # noqa: F821
            json=[
                Message(
                    user_id=str(message.author.id), message=message.content
                ).model_dump()
            ],  # noqa: F821
        )

        agent_id = resp.json()["id"]

        await thread.typing()
        while True:
            response = requests.get(
                f"{os.getenv('API_URL', 'http://localhost:8080')}/agent/{agent_id}"  # noqa: F821
            )
            final_state = response.json()
            if final_state is None:
                continue
            await thread.send(final_state)
            break


if __name__ == "__main__":
    client.run(os.getenv("DISCORD_BOT_TOKEN") or "")  # noqa: F821
