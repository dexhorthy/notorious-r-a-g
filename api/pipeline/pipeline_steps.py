import asyncio
import random
from typing import List

from socketio import AsyncServer
from baml_client.async_client import b
from baml_client.types import Context, FinalAnswer
from notorious_r_a_g.rag_simple import retrieve


async def formulate_response(sio: AsyncServer, question: str) -> str:
    await sio.emit(
        "message", {"state": "agent: formulating response", "icon": "pencil"}
    )

    context: List[Context] = []

    for i in range(5):
        resp = await b.FormulateAnswer(question, context)
        if isinstance(resp, FinalAnswer):
            await sio.emit(
                "message", {"state": "draft answer: " + resp.answer, "icon": "pencil"}
            )
            return resp.answer

        await sio.emit(
            "message",
            {
                "state": f"querying pinecone docs index: {resp.question}",
                "icon": "github",
            },
        )
        await asyncio.sleep(random.randint(1, 3))
        result = retrieve("baml", resp.question)
        context.append(Context(intent="RAGQuery", context=result))
        await sio.emit(
            "message",
            {"state": f"context: {result}", "icon": "github", "indent": 1},
        )

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


async def run_pipeline(sio, question: str):
    initial_draft = await formulate_response(sio, question)

    for state in states:
        await sio.emit("message", {"state": state.__name__})
        await asyncio.sleep(random.randint(1, 3))

    await sio.emit(
        "final_answer",
        {
            "answer": "The answer to your question '"
            + question
            + "' is: "
            + initial_draft,
        },
    )
    return question
