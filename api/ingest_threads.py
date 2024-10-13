import copy
import time
from dotenv import load_dotenv
from pinecone import ServerlessSpec, Pinecone
import os
from openai import OpenAI
import json
from tqdm import tqdm


def get_index(index_name):
    api_key = os.environ.get("PINECONE_API_KEY")

    pc = Pinecone(api_key=api_key)

    cloud = "aws"
    region = "us-east-1"

    spec = ServerlessSpec(cloud=cloud, region=region)

    # check if index already exists (it shouldn't if this is first time)
    if index_name not in pc.list_indexes().names():
        # if does not exist, create index
        pc.create_index(index_name, dimension=1536, metric="cosine", spec=spec)
        # wait for index to be initialized
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    # connect to index
    index = pc.Index(index_name)
    return index


def get_embedding(messages, client, model="text-embedding-ada-002"):
    # Remove empty messages
    messages = [m for m in messages if m["content"] != ""]

    # TODO: Right now, we are embedding the whole thread, which contains timestamp and authors.
    # See if it performs better w/o timestamps and/or authors
    text = json.dumps(messages)

    return client.embeddings.create(input=[text], model=model).data[0].embedding


def main():
    load_dotenv()

    with open("discord_json/thread_messages.json", "r") as file:
        threads = json.load(file)

    assert threads, "threads is empty!"

    client = OpenAI()

    data = []

    # Chunk 100 messages into one embedding
    message_count = 100
    for thread in tqdm(threads):

        if not thread["thread_id"]:
            continue

        for start in range(0, len(thread["messages"]), message_count):
            messages = thread["messages"][start : start + message_count]

            data.append(
                {
                    "id": str(thread["thread_id"]),
                    "values": get_embedding(messages, client),
                    "metadata": {
                        "type": "discord_thread",
                        "text": json.dumps(thread),
                        "thread_id": thread["thread_id"],
                        "thread_name": thread.get("thread name", ""),
                    },
                }
            )

    index = get_index("baml")
    index.upsert(vectors=data)
    print("Success! Updated index")


if __name__ == "__main__":
    main()
