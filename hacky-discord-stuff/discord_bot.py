import datetime
import os
import discord
from discord.ext import commands
from llama_index.readers.discord import DiscordReader
from llama_index.core import VectorStoreIndex
from dotenv import load_dotenv

load_dotenv()

discord_token = os.getenv("DISCORD_BOT_TOKEN")
channel_ids = [1119375594984050779]
reader = DiscordReader(discord_token=discord_token)
documents = reader.load_data(channel_ids=channel_ids)

import json


# Dump the documents to JSON
def dump_documents_to_json(documents, output_file="discord_documents.json"):
    json_data = []
    for doc in documents:
        metadata = doc.metadata.copy()
        # Convert datetime objects to ISO format strings
        for key, value in metadata.items():
            if isinstance(value, datetime.datetime):
                metadata[key] = value.isoformat()

        json_data.append({"text": doc.text, "metadata": metadata})

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    print(f"Documents dumped to {output_file}")


# Call the function to dump documents
dump_documents_to_json(documents)


# Create an index from the loaded documents
index = VectorStoreIndex.from_documents(documents)

# Create a query engine
query_engine = index.as_query_engine()


# Function to query the documents
def query_documents(query_text):
    response = query_engine.query(query_text)
    return response


# Example usage
example_query = "What are the main topics discussed in the Discord channel?"
result = query_documents(example_query)
print(f"Query: {example_query}")
print(f"Result: {result}")
