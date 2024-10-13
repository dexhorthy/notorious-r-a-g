import asyncio
import logging
import random
from typing import Callable, List

from pipeline.db import AgentStateManager
from baml_client.async_client import b
from baml_client.types import Context, FinalAnswer
from notorious_r_a_g.rag_simple import retrieve
from models import Message

from humanlayer import HumanLayer, ContactChannel, SlackContactChannel

logger = logging.getLogger(__name__)

hl = HumanLayer(
    verbose=True,
    contact_channel=ContactChannel(
        slack=SlackContactChannel(
            channel_or_user_id="C07RMGJRMMY",
            experimental_slack_blocks=True,
        )
    ),
)


async def run_async(func: Callable, *args):  # noqa: F821
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)


# run_async doesn't support **kwargs, so we need a wrapper, because openai function calling
# doesn't support *args
def submit_answer_wrapper(question: str, answer: str) -> tuple[str, str] | str:
    return submit_answer(question=question, answer=answer)


@hl.require_approval()
def submit_answer(question: str, answer: str) -> tuple[str, str] | str:
    return "done", answer


async def formulate_response(sio: AgentStateManager, question: str) -> str:
    sio.add_action(type="formulate_response", content="Formulating response")

    context: List[Context] = []

    for i in range(15):
        resp = await b.FormulateAnswer(question, context)
        if isinstance(resp, FinalAnswer):
            sio.add_action(type="HumanApproval", content=resp.answer)
            res = await run_async(submit_answer_wrapper, question, resp.answer)
            if isinstance(res, tuple):
                sio.add_action(type="Finalizing Answer", content=res[1])
                return res[1]
            else:
                sio.add_action(type="Incorporating Feedback", content=res)
                context.append(Context(intent="Draft Answer", context=resp.answer))
                context.append(Context(intent="Feedback from admin", context=res))
        else:
            sio.add_action(
                type="RAGQuery",
                content=f"Querying pinecone docs index: {resp.question}",
            )

            await asyncio.sleep(random.randint(1, 3))
            result = await run_async(retrieve, "baml", resp.question)
            context.append(Context(intent="RAGQuery", context=result))
            sio.add_action(type="RAGResult", content=f"Result from RAG: {result}")

    raise Exception("No answer found")


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
    try:
        initial_draft = await formulate_response(sio, question)
    except Exception:
        logger.error("Error formulating response", exc_info=True)
        sio.cancel()
        return

    for s in states:
        sio.add_action(type=s.__name__, content=f"Result from {s.__name__}")
        await asyncio.sleep(random.randint(1, 3))

    sio.complete(initial_draft)
