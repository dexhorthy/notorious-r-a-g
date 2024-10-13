from datetime import datetime
import json
from pydantic import BaseModel
from typing import List, Literal, Optional
from firebase_admin import firestore, initialize_app
from baml_client.types import Classification
from models import Message

initialize_app()


StateName = Literal["running", "completed", "failed", "cancelled", "paused"]
FinalState = str

class InitialState(BaseModel):
    messages: List[Message]
    classification: Classification


class Action(BaseModel):
    type: str
    content: str
    create_time_ms: Optional[int] = None


class AgentState(BaseModel):
    create_time_ms: Optional[int] = None
    update_time_ms: Optional[int] = None
    state: StateName
    initial_state: InitialState
    actions: list[Action]
    final_state: Optional[FinalState]

    @staticmethod
    def create(start: InitialState):
        now = int(datetime.utcnow().timestamp() * 1000)
        return AgentState(
            state="running",
            initial_state=start,
            actions=[],
            final_state=None,
            create_time_ms=now,
            update_time_ms=now,
        )


COLLECTION = "agentstate"


class AgentStateManager:
    """
    Manages saving agent states to Firestore with each incremental update.
    """

    def __init__(
        self, doc_ref: firestore.firestore.DocumentReference, action: AgentState
    ):
        self.__doc_ref = doc_ref
        self.__data = action

    @staticmethod
    def create(start: InitialState):
        action = AgentState.create(start)
        db = firestore.client()
        collection_ref = db.collection(COLLECTION)
        doc_ref = collection_ref.document()  # Auto-generates an ID
        doc_ref.set(action.model_dump())
        return AgentStateManager(doc_ref, action)

    @staticmethod
    def from_id(id: str):
        db = firestore.client()
        doc_ref = db.collection(COLLECTION).document(id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            assert data is not None
            action = AgentState(**data)
            return AgentStateManager(doc_ref, action)
        else:
            raise ValueError(f"Id {id} does not exist")

    def final_state(self) -> FinalState | None:
        if self.__data.state == "cancelled":
            return "sorry, I couldn't get an answer"
        return self.__data.final_state

    def id(self) -> str:
        return self.__doc_ref.id

    def add_action(self, *, type: str, content: str):
        if type == "HumanApproval":
            self.__data.state = "paused"
        else:
            self.__data.state = "running"
        self.__data.actions.append(
            Action(
                type=type,
                content=content,
                create_time_ms=int(datetime.utcnow().timestamp() * 1000),
            )
        )
        self.__doc_ref.set(self.__data.model_dump())

    def cancel(self, message: str):
        self.__data.state = "cancelled"
        self.__data.update_time_ms = int(datetime.utcnow().timestamp() * 1000)
        self.__data.final_state = message
        self.__doc_ref.set(self.__data.model_dump())

    def complete(self, final_state: FinalState):
        self.__data.state = "completed"
        self.__data.final_state = final_state
        self.__data.update_time_ms = int(datetime.utcnow().timestamp() * 1000)
        self.__doc_ref.set(self.__data.model_dump())
