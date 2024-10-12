import json
from pydantic import BaseModel
from typing import List, Literal, Optional
from firebase_admin import firestore, initialize_app
from models import Message
initialize_app()


StateName = Literal['running', 'completed', 'failed', 'cancelled']
InitialState = List[Message]
FinalState = str

class Action(BaseModel):
    type: str
    content: str

class AgentState(BaseModel):
    state: StateName
    initial_state: InitialState
    actions: list[Action]
    final_state: Optional[FinalState]

    @staticmethod
    def create(start: InitialState):
        return AgentState(
            state='running',
            initial_state=start,
            actions=[],
            final_state=None
        )

COLLECTION = "agentstate"

class AgentStateManager:
    """
    Manages saving agent states to Firestore with each incremental update.
    """
    def __init__(self, doc_ref: firestore.firestore.DocumentReference, action: AgentState):
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

    def id(self) -> str:
        return self.__doc_ref.id

    def add_action(self, *, type: str, content: str):
        self.__data.actions.append(Action(type=type, content=content))
        self.__doc_ref.set(self.__data.model_dump())

    def cancel(self):
        self.__data.state = 'cancelled'
        self.__doc_ref.set(self.__data.model_dump())

    def complete(self, final_state: FinalState):
        self.__data.state = 'completed'
        self.__data.final_state = final_state
        self.__doc_ref.set(self.__data.model_dump())
