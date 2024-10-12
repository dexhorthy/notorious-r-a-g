from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding

import os
import json
import uuid

data = []

# Load all documents from crawled_docs directory
crawled_docs_dir = os.path.join(os.path.dirname(__file__), 'crawled_docs')
from tqdm import tqdm

for filename in tqdm(os.listdir(crawled_docs_dir), desc="Processing files"):
    if filename.endswith('.json'):
        file_path = os.path.join(crawled_docs_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            doc = json.load(f)
            # Assuming the crawled document has a 'content' field
            if 'markdown' in doc and doc['metadata']['statusCode'] != 404:
                data.append({
                    'id': str(uuid.uuid4()),
                    'values': get_embedding(doc['markdown']),
                    'metadata': {'text': doc['markdown'], 'type': 'docs', 'url': doc['metadata']['ogUrl'], 'title': doc['metadata']['ogTitle']}
                })

# If no documents were found, print a warning
if not data:
    print("Warning: No documents found in the crawled_docs directory.")

import time
from pinecone import ServerlessSpec, Pinecone
import os

def get_index(index_name):
    api_key = os.environ.get('PINECONE_API_KEY')

    pc = Pinecone(api_key=api_key)

    cloud = 'aws'
    region = 'us-east-1'

    spec = ServerlessSpec(cloud=cloud, region=region)

    # check if index already exists (it shouldn't if this is first time)
    if index_name not in pc.list_indexes().names():
        # if does not exist, create index
        pc.create_index(
            index_name,
            dimension=1536,
            metric='cosine',
            spec=spec
        )
        # wait for index to be initialized
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)

    # connect to index
    index = pc.Index(index_name)

    index.upsert(vectors=data)

def retrieve(index, query):
    limit = 3750
    res = get_embedding(query)

    # get relevant contexts
    res = index.query(vector=res, top_k=3, include_metadata=True)
    contexts = [
        x['metadata']['text'] for x in res['matches']
    ]
    # build our prompt with the retrieved contexts included
    prompt_start = (
        "Answer the question based on the context below.\n\n"+
        "Context:\n"
    )
    prompt_end = (
        f"\n\nQuestion: {query}\nAnswer:"
    )
    # append contexts until hitting limit
    for i in range(1, len(contexts)):
        if len("\n\n---\n\n".join(contexts[:i])) >= limit:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts[:i-1]) +
                prompt_end
            )
            break
        elif i == len(contexts)-1:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts) +
                prompt_end
            )
    return prompt

def query(index, prompt):
    prompt = retrieve(index, prompt)
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    )
    return completion.choices[0].message.content


index = get_index("baml")
# query = "who is alice?"
# prompt = retrieve(index, query)
# print(query(index, prompt))