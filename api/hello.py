from contextlib import asynccontextmanager
import os
from discord_thread import launch_discord_listener
from pipeline.pipeline_steps import run_pipeline
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pipeline.db import AgentStateManager
from pydantic import BaseModel
from typing import List
import socketio
import uvicorn
from models import Message

from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager  # noqa: F821
async def lifespan(app: FastAPI):
    # await launch_discord_listener(os.getenv("DISCORD_BOT_TOKEN"))
    yield


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
async def start_agent(messages: str | List[Message], background_tasks: BackgroundTasks) -> str:
    if isinstance(messages, str):
        messages = [Message(user_id="web_app", message=messages)]
    state = AgentStateManager.create(messages)
    background_tasks.add_task(run_pipeline, state, messages)
    return state.id()


# @app.get("/questions", response_model=List[Question])
# async def read_questions():
#     return questions


# @app.get("/questions/{question_id}", response_model=Question)
# async def read_question(question_id: int):
#     for question in questions:
#         if question.id == question_id:
#             return question
#     return {"error": "Question not found"}


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


if __name__ == "__main__":
    uvicorn.run("hello:app", host="0.0.0.0", port=8080, reload=True)
