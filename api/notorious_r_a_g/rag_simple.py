from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


import time
from pinecone import ServerlessSpec, Pinecone
import os


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


def retrieve(index_name: str, query: str) -> str:
    limit = 3750
    res = get_embedding(query)

    # get relevant contexts
    res = get_index(index_name).query(vector=res, top_k=3, include_metadata=True)
    contexts = [x.get("metadata", {}).get("text") for x in res["matches"]]
    # build our prompt with the retrieved contexts included
    prompt_start = ""
    prompt_end = ""
    # append contexts until hitting limit
    for i in range(1, len(contexts)):
        if len("\n\n---\n\n".join(contexts[:i])) >= limit:
            prompt = prompt_start + "\n\n---\n\n".join(contexts[: i - 1]) + prompt_end
            break
        elif i == len(contexts) - 1:
            prompt = prompt_start + "\n\n---\n\n".join(contexts) + prompt_end
    return prompt


def query(index_name: str, prompt: str) -> str:
    prompt = retrieve(index_name, prompt)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    assert completion.choices[0].message.content is not None
    return completion.choices[0].message.content
