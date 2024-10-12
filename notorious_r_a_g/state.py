# state.py
import os

from notorious_r_a_g.baml_client.async_client import b
from notorious_r_a_g.baml_client.types import Message

import reflex as rx


class State(rx.State):
    # The current question being asked.
    question: str

    # Keep track of the chat history as a list of (question, answer) tuples.
    chat_history: list[tuple[str, str]]

    async def answer(self):
        # Our chatbot has some brains now!
        session = b.stream.BasicChat([Message(role="user", content=self.question)])


        # Add to the answer as the chatbot responds.
        answer = ""
        self.chat_history.append((self.question, answer))

        # Clear the question input.
        self.question = ""
        # Yield here to clear the frontend input before continuing.
        yield

        async for item in session:
            if item:
                self.chat_history[-1] = (
                    self.chat_history[-1][0],
                    item,
                )
                yield
