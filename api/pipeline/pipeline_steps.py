import asyncio
import logging
import random
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, TypeVar

from openai import BaseModel
from pipeline.db import RagItem
from pipeline.db import RagResult
from notorious_r_a_g.rag_simple import retrieve_llamaindex

from pipeline.db import AgentStateManager
from baml_client.async_client import b
from baml_py.errors import BamlValidationError
from baml_client.types import Context, ReadyToAnswer
from models import Message

from humanlayer import HumanLayer, ContactChannel, ResponseOption, SlackContactChannel

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


# @hl.require_approval(reject_options=[ResponseOption(name="request_changes", title="Request Changes"), ResponseOption(name="take_over", title="I'll Take Over", prompt_fill="MY_EXIT_PROMPT")])
def submit_answer(*, question: str, answer: str) -> tuple[str, str] | str:
    return "done", answer


async def get_human_approval(question: str, answer: str) -> str | tuple[str, str]:
    res = submit_answer(question=question, answer=answer)
    return res


class ContextManager:
    def __init__(self):
        self.__contexts = []

    def add_context(self, intent: str, context: str):
        self.__contexts.append(Context(intent=intent, context=context))

    def get_contexts(self) -> List[Context]:
        return self.__contexts

class HumanApproval(BaseModel):
    approved: bool
    feedback: Optional[str]
    function_name: str
    kwargs: Dict[str, Any]


async def on_human_approval(id: str, status: HumanApproval) -> None:
    if status.function_name == "submit_answer":
        sio = AgentStateManager.from_id(id)
        if status.approved:
            param = status.kwargs["answer"]
            sio.add_action(type="Finalizing Answer", content=param)
            sio.complete(param)
        else:
            assert status.feedback
            if "MY_EXIT_PROMPT" in status.feedback:
                sio.cancel(message="Human took over")
                return
            else:
                context = sio.get_context()
                question = sio.get_question()
                context.add_context(intent="Draft Answer", context=status.kwargs["answer"])
                context.add_context(intent="Feedback from admin", context=status.feedback)
                sio.add_action(type="Incorporating Feedback", content=status.feedback)
                await formulate_response(sio, question, context)

T = TypeVar('T')

class ResponseType(Generic[T]):
    def __init__(self, response: T | HumanLayerMessage):
        if isinstance(response, HumanLayerMessage):
            self.__response = None
            self.__hl_message = response
        else:
            self.__response = response
            self.__hl_message = None

    def get_response(self) -> T:
        if self.__hl_message is None:
            return self.__response # type: ignore
        raise Exception("Response is a HumanLayerMessage")

    def get_hl_message(self) -> HumanLayerMessage:
        if self.__hl_message is not None:
            return self.__hl_message
        raise Exception("Response is not a HumanLayerMessage")
    




async def formulate_response(sio: AgentStateManager, question: str, context: ContextManager) -> ResponseType[str]:
    sio.add_action(type="formulate_response", content="Formulating response")

    max_steps = 5

    while max_steps > 0:
        max_steps -= 1
        try:
            resp = await b.FormulateAnswer(question, context.get_contexts())
        except BamlValidationError as e:
            sio.add_action(type="Error", content=str(e))
            context.add_context(intent="Note", context="Be sure to respond with the right format")
            continue
        if isinstance(resp, ReadyToAnswer):
            sio.add_action(type="ReadyToAnswer", content=resp.reason)
            answer = await b.AnswerQuestion(question, context.get_contexts())
            sio.add_action(type="HumanApproval", content=answer)
            return await ping_human_layer(...)
        else:
            sio.add_action(
                type="RAGQuery",
                content=f'Filtered: {resp.filter_to}\n{resp.question}',
            )
            result = await run_async(retrieve_llamaindex, "baml2", resp.question, resp.filter_to)

            def make_rag_prompt(contexts: List[Tuple[str, dict]]) -> str:
                # append contexts until hitting limit
                limit = 3750
                prompt = "No relevant information found."
                accumulated_length = 0
                selected_contexts = []

                for (context, meta) in contexts:
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

            context.add_context(intent="RAGQuery", context=make_rag_prompt(result))
            sio.add_action(type="RAGResult", content=RagResult(result=[RagItem(content=content, metadata=metadata) for content, metadata in result]))

    raise Exception("No answer found")


async def run_pipeline(sio: AgentStateManager, questions: List[Message]):
    question = questions[0].message
    context = ContextManager()
    try:
        initial_draft = await formulate_response(sio, question, context)
    except Exception as e:
        sio.cancel(message=str(e))
        return
    
    draft = initial_draft.get_response()
    sio.complete(draft)
