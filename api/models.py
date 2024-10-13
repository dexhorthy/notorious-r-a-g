from pydantic import BaseModel


class Message(BaseModel):
    user_id: str
    message: str
    avatar_url: str | None = None
    name: str | None = None

