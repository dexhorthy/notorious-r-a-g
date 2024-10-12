import asyncio
import random
from typing import List

from socketio import AsyncServer
from pipeline.db import AgentStateManager
from baml_client.async_client import b
from baml_client.types import Context, FinalAnswer
from notorious_r_a_g.rag_simple import retrieve
from models import Message


async def formulate_response(sio: AgentStateManager, question: str) -> str:
    sio.add_action(type="formulate_response", content="Formulating response")

    context: List[Context] = []

    for i in range(5):
        resp = await b.FormulateAnswer(question, context)
        if isinstance(resp, FinalAnswer):
            return resp.answer

        sio.add_action(type="RAGQuery", content=f"Querying pinecone docs index: {resp.question}")

        await asyncio.sleep(random.randint(1, 3))
        result = retrieve("baml", resp.question)
        context.append(Context(intent="RAGQuery", context=result))
        sio.add_action(type="RAGResult", content=f"Result from RAG: {result}")

    return "giving up, no answer found"


def attach_docs_and_sources():
    # Logic for attaching docs and sources
    pass


def review_answer():
    # Logic for reviewing answer
    pass


def get_human_feedback():
    # Logic for getting human feedback
    pass


def mark_as_done():
    # Logic for marking the process as done
    pass


states = [
    attach_docs_and_sources,
    review_answer,
    get_human_feedback,
    mark_as_done,
]


async def run_pipeline(sio: AgentStateManager, questions: List[Message]):
    question = questions[0].message
    initial_draft = await formulate_response(sio, question)

    for s in states:
        sio.add_action(type=s.__name__, content=f"Result from {s.__name__}")
        await asyncio.sleep(random.randint(1, 3))

    sio.complete(initial_draft)
