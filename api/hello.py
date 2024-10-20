import asyncio
import os

from contextlib import asynccontextmanager
from baml_client.types import QuestionType
from discord_thread import run_bot
from baml_client.types import Classification
from pipeline.pipeline_steps import run_pipeline
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pipeline.db import AgentStateManager, FinalState, InitialState
from pydantic import BaseModel
from typing import List
import uvicorn
from models import Message
from baml_client import b

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(run_bot())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

# Create a Socket.IO AsyncServer instance
# sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

# Wrap the FastAPI app with Socket.IO
# socket_app = socketio.ASGIApp(sio, app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/agent")
async def start_agent(
    messages: str | List[Message], background_tasks: BackgroundTasks
) -> dict[str, str]:
    if isinstance(messages, str):
        messages = [Message(user_id="web_app", message=messages)]
    try:
        classification = b.ClassifyMessage(messages)
    except Exception as e:
        classification = Classification(intent=QuestionType.Troubleshooting, title=messages[0].message[:20])
    if isinstance(classification, Classification):
        state = AgentStateManager.create(InitialState(messages=messages, classification=classification))
        background_tasks.add_task(run_pipeline, state, messages)
        return {"id": state.id(), "title": classification.title}
    else:
        return {"ignore_reason": classification.value}


@app.get("/agent/{agent_id}")
async def read_agent(agent_id: str) -> FinalState | None:
    state = AgentStateManager.from_id(agent_id)
    return state.final_state()


# Socket.IO event handlers
# @sio.event
# async def connect(sid, environ):
#     print(f"Client connected: {sid}")


# @sio.event
# async def disconnect(sid):
#     print(f"Client disconnected: {sid}")


# @sio.event
# async def message(sid, data):
#     print(f"Received message from {sid}: {data}")
#     await create_question(Question(id=len(questions), text=data["text"]))

# where the magic happens
# register an asyncio.create_task(client.start()) on app's startup event
#                                        ^ note not client.run()



if __name__ == "__main__":
    uvicorn.run("hello:app", host="0.0.0.0", port=int(os.getenv("PORT", "8080")), reload=True)
