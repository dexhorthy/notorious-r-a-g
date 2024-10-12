from pydantic import BaseModel


class Message(BaseModel):
    user_id: str
    message: str

