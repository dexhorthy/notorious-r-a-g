from typing import Dict, List, Tuple, cast
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)
from llama_index.core.schema import NodeWithScore
from openai import OpenAI
from baml_client.types import Source

from dotenv import load_dotenv

from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from phoenix.otel import register

tracer_provider = register(
  project_name="notorious-RAG", # Default is 'default'
  endpoint="http://localhost:6006/v1/traces",
)

LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)


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

def filter_to_str(filter_to: Source) -> str:
    if filter_to == Source.Documentation:
        return "docs"
    elif filter_to == Source.Discord:
        return "discord_thread"
    raise ValueError(f"Unknown source: {filter_to}")
        
    

def retrieve_llamaindex(index_name: str, query: str, filter_to: List[Source]) -> List[Tuple[str, Dict[str, str]]]:
    from llama_index.core import VectorStoreIndex
    from llama_index.vector_stores.pinecone import PineconeVectorStore

    vector_store = PineconeVectorStore(index_name=index_name)
    from llama_index.embeddings.openai import OpenAIEmbedding
    embed_model = OpenAIEmbedding(model="text-embedding-ada-002")
    index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
    if len(filter_to) == 0 or len(filter_to) == len(Source):
        filters = None
    else:
        filters = MetadataFilters(
            filters=[
                MetadataFilter(
                    key="type", operator=FilterOperator.IN, value=[filter_to_str(x) for x in filter_to]
                ),
            ]
        )

    retriever = index.as_retriever(similarity_top_k=5, filters=filters)
    top_results: List[NodeWithScore] = retriever.retrieve(query)
    for result in top_results:
        print(result.node.get_content())
    contexts = [(result.node.get_content(), cast(Dict[str, str], result.node.metadata)) for result in top_results]
    return contexts

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
