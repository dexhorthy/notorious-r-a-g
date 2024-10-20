import asyncio
import logging
import random
from typing import Callable, List, Tuple
from pipeline.db import RagItem
from pipeline.db import RagResult
from notorious_r_a_g.rag_simple import retrieve_llamaindex

from pipeline.db import AgentStateManager
from baml_client.async_client import b
from baml_client.types import Context, FinalAnswer
from models import Message

from humanlayer import (
    FunctionCallSpec,
    FunctionCallStatus,
    HumanLayer,
    ContactChannel,
    ResponseOption,
    SlackContactChannel,
)

logger = logging.getLogger(__name__)

humanlayer_channel = ContactChannel(
    slack=SlackContactChannel(
        channel_or_user_id="C07RMGJRMMY",
        experimental_slack_blocks=True,
    )
)


hl = HumanLayer(
    verbose=True,
    contact_channel=humanlayer_channel,
)


async def run_async(func: Callable, *args):  # noqa: F821
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)


async def run_approval(
    question: str, answer: str
) -> FunctionCallStatus.Approved | FunctionCallStatus.Rejected:
    return (
        await run_async(
            hl.fetch_approval,
            FunctionCallSpec(
                fn="submit_answer",
                kwargs={
                    "question": question,
                    "answer": answer,
                },
                reject_options=[
                    ResponseOption(
                        name="request_changes",
                        title="Request changes",
                    ),
                    ResponseOption(
                        name="human_takeover",
                        title="I'll take over",
                        prompt_fill="MY_EXIT_PROMPT",
                    ),
                ],
            ),
        )
    ).as_completed()


async def formulate_response(sio: AgentStateManager, question: str) -> str:
    sio.add_action(type="formulate_response", content="Formulating response")

    context: List[Context] = []

    max_steps = 5

    while max_steps > 0:
        max_steps -= 1
        resp = await b.FormulateAnswer(question, context)
        if isinstance(resp, FinalAnswer):
            sio.add_action(type="ReadyToAnswer", content=resp.reason)
            answer: str = await b.AnswerQuestion(question, context)
            sio.add_action(type="HumanApproval", content=answer)

            approval_result = await run_approval(question, answer)

            if approval_result.approved is True:
                sio.add_action(type="FinalAnswer", content=answer)
                return answer
            else:
                if "MY_EXIT_PROMPT" in approval_result.comment:
                    raise Exception("Human took over")
                sio.add_action(
                    type="Incorporating Feedback",
                    content=f"Admin denied FinalAnswer with feedback: {approval_result.comment}",
                )
                context.append(Context(intent="Draft Answer", context=answer))
                context.append(
                    Context(
                        intent="Feedback from admin",
                        context=f"Admin denied FinalAnswer with feedback: {approval_result.comment}",
                    )
                )
                # Reset max_steps to 5 after a human gives feedback
                max_steps = 5
        else:
            sio.add_action(
                type="RAGQuery",
                content=f"Filtered: {resp.filter_to}\n{resp.question}",
            )
            result = await run_async(
                retrieve_llamaindex, "baml2", resp.question, resp.filter_to
            )

            def make_rag_prompt(contexts: List[Tuple[str, dict]]) -> str:
                # append contexts until hitting limit
                limit = 3750
                prompt = "No relevant information found."
                accumulated_length = 0
                selected_contexts = []

                for context, meta in contexts:
                    context_length = len(context) + len("\n\n---\n\n")
                    if accumulated_length + context_length > limit:
                        # Truncate the context to fit within the limit
                        remaining_space = limit - accumulated_length
                        truncated_context = context[
                            : remaining_space - len("\n\n---\n\n")
                        ]
                        selected_contexts.append(truncated_context)
                        break
                    selected_contexts.append(context)
                    accumulated_length += context_length

                if selected_contexts:
                    prompt = "\n\n---\n\n".join(selected_contexts)

                return prompt

            context.append(Context(intent="RAGQuery", context=make_rag_prompt(result)))
            sio.add_action(
                type="RAGResult",
                content=RagResult(
                    result=[
                        RagItem(content=content, metadata=metadata)
                        for content, metadata in result
                    ]
                ),
            )

    raise Exception("No answer found")


async def run_pipeline(sio: AgentStateManager, questions: List[Message]):
    question = questions[0].message
    try:
        initial_draft = await formulate_response(sio, question)
    except Exception as e:
        sio.cancel(message=str(e))
        return

    print("COMPLETING - ", initial_draft)
    sio.complete(initial_draft)
