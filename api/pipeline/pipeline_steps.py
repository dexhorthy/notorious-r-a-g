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
def submit_answer(*, question: str, answer: str) -> tuple[str, str] | str:
    return "done", answer


async def get_human_approval(question: str, answer: str) -> str | tuple[str, str]:
    res = submit_answer(question=question, answer=answer)
    return res


async def formulate_response(sio: AgentStateManager, question: str) -> str:
    sio.add_action(type="formulate_response", content="Formulating response")

    context: List[Context] = []

    max_steps = 5

    while max_steps > 0:
        max_steps -= 1
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
                # Reset max_steps to 5 after a human gives feedback
                max_steps = 5
        else:
            sio.add_action(
                type="RAGQuery",
                content=f"Querying pinecone docs index: {resp.question}",
            )
            result = await run_async(retrieve, "baml", resp.question)
            context.append(Context(intent="RAGQuery", context=result))
            sio.add_action(type="RAGResult", content=f"Result from RAG: {result}")

    raise Exception("No answer found")


async def run_pipeline(sio: AgentStateManager, questions: List[Message]):
    question = questions[0].message
    try:
        initial_draft = await formulate_response(sio, question)
    except Exception as e:
        sio.cancel(message=str(e))
        return

    sio.complete(initial_draft)
