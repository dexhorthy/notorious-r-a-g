import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.channel.id not in [1294545886281469972]:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")


async def launch_discord_listener(discord_token):
    await client.start(discord_token)
