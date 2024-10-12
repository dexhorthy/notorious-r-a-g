import asyncio
import random
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import socketio
import uvicorn

from pipeline.pipeline_steps import run_pipeline

app = FastAPI()

# Create a Socket.IO AsyncServer instance
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

# Wrap the FastAPI app with Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class Question(BaseModel):
    id: int
    text: str
    events: List[str] = []


questions = []


@app.post("/questions", response_model=Question)
async def create_question(question: Question):
    questions.append(question)
    await run_pipeline(sio, question.text)


@app.get("/questions", response_model=List[Question])
async def read_questions():
    return questions


@app.get("/questions/{question_id}", response_model=Question)
async def read_question(question_id: int):
    for question in questions:
        if question.id == question_id:
            return question
    return {"error": "Question not found"}


# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.event
async def message(sid, data):
    print(f"Received message from {sid}: {data}")
    await create_question(Question(id=len(questions), text=data["text"]))


if __name__ == "__main__":
    uvicorn.run("hello:socket_app", host="0.0.0.0", port=8080, reload=True)
