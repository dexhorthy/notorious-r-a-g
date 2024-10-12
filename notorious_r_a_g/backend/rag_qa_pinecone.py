import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables
pinecone_api_key = os.getenv('PINECONE_API_KEY')
hf_token = os.getenv('HF_TOKEN')
llama_cloud_api_key = os.getenv('LLAMA_CLOUD_API_KEY')
mistral_api_key = os.getenv('MISTRAL_API_KEY')

from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.embeddings.mistralai import MistralAIEmbedding
from llama_index.core.workflow import Event
from llama_index.core.schema import NodeWithScore
from llama_index.core import PromptTemplate

class PrepEvent(Event):
    """Prep event (prepares for retrieval)."""
    pass

class RetrieveEvent(Event):
    """Retrieve event (gets retrieved nodes)."""

    retrieved_nodes: list[NodeWithScore]

class AugmentGenerateEvent(Event):
    """Query event. Queries given relevant text and search text."""
    relevant_text: str
    search_text: str

DEFAULT_RAG_PROMPT = PromptTemplate(
    template="""Use the provided context to answer the question. If you don't know the answer, say you don't know.

    Context:
    {context}

    Question:
    {question}
    """
)

from llama_index.core.workflow import (
    Workflow,
    step,
    Context,
    StartEvent,
    StopEvent,
)
from llama_index.core import (
    VectorStoreIndex,
    Document,
    SummaryIndex,
)
from llama_index.core.query_pipeline import QueryPipeline
from llama_index.llms.openai import OpenAI
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.pinecone import PineconeVectorStore
from IPython.display import Markdown, display
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.llms.text_generation_inference import (
    TextGenerationInference,
)

parser = LlamaParse(
result_type="markdown",
api_key=llama_cloud_api_key
)

file_extractor = {".pdf": parser}
all_documents = SimpleDirectoryReader(input_files=['./file_with_info.pdf'], file_extractor=file_extractor).load_data()
print(len(all_documents))

model_name="mistral-embed"
embed_model = MistralAIEmbedding(model_name=model_name, api_key=mistral_api_key)
embedding_dimension = 1024
Settings.embed_model = embed_model

from pinecone import Pinecone, ServerlessSpec
pc = Pinecone(api_key=pinecone_api_key)

index_name = "discord-bot-hackathon"
# pc.create_index(
#     name=index_name,
#     dimension=embedding_dimension,
#     metric="cosine",
#     spec=ServerlessSpec(
#         cloud="aws",
#         region="us-east-1"
#     )
# )

pinecone_index = pc.Index(index_name)

class OpenSourceRAG(Workflow):
    @step
    async def ingest(self, ctx: Context, ev: StartEvent) -> StopEvent | None:
        """Ingest step (for ingesting docs and initializing index)."""
        documents: list[Document] | None = ev.get("documents")

        if documents is None:
            return None

        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )

        return StopEvent(result=index)

    @step
    async def prepare_for_retrieval(
        self, ctx: Context, ev: StartEvent
    ) -> PrepEvent | None:
        """Prepare for retrieval."""

        model_url = "https://bzpz92sw0xhmybii.us-east-1.aws.endpoints.huggingface.cloud"

        query_str: str | None = ev.get("query_str")
        retriever_kwargs: dict | None = ev.get("retriever_kwargs", {})

        if query_str is None:
            return None

        index = ev.get("index")

        llm = TextGenerationInference(
            model_url=model_url,
            token=hf_token,
            model_name="hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4"
        )
        await ctx.set("rag_pipeline", QueryPipeline(
            chain=[DEFAULT_RAG_PROMPT, llm]
        ))

        await ctx.set("llm", llm)
        await ctx.set("index", index)

        await ctx.set("query_str", query_str)
        await ctx.set("retriever_kwargs", retriever_kwargs)

        return PrepEvent()

    @step
    async def retrieve(
        self, ctx: Context, ev: PrepEvent
    ) -> RetrieveEvent | None:
        """Retrieve the relevant nodes for the query."""
        query_str = await ctx.get("query_str")
        retriever_kwargs = await ctx.get("retriever_kwargs")

        if query_str is None:
            return None

        index = await ctx.get("index", default=None)
        if not (index):
            raise ValueError(
                "Index and tavily tool must be constructed. Run with 'documents' and 'tavily_ai_apikey' params first."
            )

        retriever: BaseRetriever = index.as_retriever(
            **retriever_kwargs
        )
        result = retriever.retrieve(query_str)
        await ctx.set("query_str", query_str)
        return RetrieveEvent(retrieved_nodes=result)

    @step
    async def augment_and_generate(self, ctx: Context, ev: RetrieveEvent) -> StopEvent:
        """Get result with relevant text."""
        relevant_nodes = ev.retrieved_nodes
        relevant_text = "\n".join([node.get_content() for node in relevant_nodes])
        query_str = await ctx.get("query_str")

        relevancy_pipeline = await ctx.get("rag_pipeline")

        relevancy = relevancy_pipeline.run(
                context=relevant_text, question=query_str
        )

        return StopEvent(result=relevancy.message.content)

async def main():
    rag_workflow = OpenSourceRAG()
    index = await rag_workflow.run(documents=all_documents)

    response = await rag_workflow.run(
    query_str="How can we win this hackathon?",
    index=index,
    )
    print(response)

# Run the async function
import asyncio
asyncio.run(main())
