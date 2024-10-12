import discord

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

    if (message.channel.id not in [1294545886281469972]) and message.channel.parent.id not in [1294545886281469972]:
        return
    if isinstance(message.channel, discord.Thread):
        thread = message.channel
        print(thread.name)
        await thread.send(f"Responding in the thread: {thread.name}")
    else:
        # Create a new thread for the question
        thread = await message.create_thread(name="New Question Thread", auto_archive_duration=60)
        await thread.send("Hello! I've created a new thread for your question. How can I assist you?")


async def launch_discord_listener(discord_token):
    await client.start(discord_token)
