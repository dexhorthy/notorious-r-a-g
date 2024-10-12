import asyncio
import random


def parse_question():
    # Logic for parsing question
    pass

def formulate_response():
    # Logic for formulating response
    pass

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
    parse_question,
    formulate_response,
    attach_docs_and_sources,
    review_answer,
    get_human_feedback,
    mark_as_done
]



async def run_pipeline(sio, question):

    for state in ["parsing question", "agent: formulating response", "agent: attaching docs and sources", "agent: reviewing answer", "agent: getting human feedback", "done"]:
        await sio.emit('message', {
            "state": state
        })
        await asyncio.sleep(random.randint(1, 3))
        question.events.append(state)
    await sio.emit('final_answer', {
        "id": question.id,
        "answer": "The answer to your question '" + question.text + "' is: you must be a bad developer then."
    })
    return question