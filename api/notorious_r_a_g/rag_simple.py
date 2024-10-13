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
    res = get_embedding(query)

    # get relevant contexts
    res = get_index(index_name).query(vector=res, top_k=3, include_metadata=True)
    contexts = [x.get("metadata", {}).get("text") for x in res["matches"]]
    print(f"Found {len(contexts)} contexts for query: {query}")
    # build our prompt with the retrieved contexts included
    
    # append contexts until hitting limit
    limit = 3750
    prompt = "No relevant information found."
    accumulated_length = 0
    selected_contexts = []

    for context in contexts:
        context_length = len(context) + len("\n\n---\n\n")
        if accumulated_length + context_length > limit:
            # Truncate the context to fit within the limit
            remaining_space = limit - accumulated_length
            truncated_context = context[:remaining_space - len("\n\n---\n\n")]
            selected_contexts.append(truncated_context)
            break
        selected_contexts.append(context)
        accumulated_length += context_length

    if selected_contexts:
        prompt = "\n\n---\n\n".join(selected_contexts)

    return prompt

def retrieve_llamaindex(index_name: str, query: str) -> str:
    from llama_index.core import VectorStoreIndex
    from llama_index.vector_stores.pinecone import PineconeVectorStore

    vector_store = PineconeVectorStore(index_name="baml")
    from llama_index.embeddings.openai import OpenAIEmbedding
    embed_model = OpenAIEmbedding(model="text-embedding-ada-002")
    index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
    retriever = index.as_retriever(similarity_top_k=3)
    top_results = retriever.retrieve("how to handle enums?")
    contexts = [top_results.node.get_content() for result in top_results]
    # build our prompt with the retrieved contexts included
    prompt_start = ""
    prompt_end = ""
    prompt = ""
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
