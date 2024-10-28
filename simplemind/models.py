import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from pydantic import BaseModel, Field

from .utils import find_provider


class SMBaseModel(BaseModel):
    date_created: datetime = Field(default_factory=datetime.now)

    def __str__(self):
        return f"<{self.__class__.__name__} {self.model_dump_json()}>"


class Message(SMBaseModel):
    role: str
    text: str
    meta: Dict[str, Any] = {}
    raw: Optional[Any] = None
    llm_model: Optional[str] = None
    llm_provider: Optional[str] = None

    def __str__(self):
        return f"<Message role={self.role} text={self.text!r}>"

    @classmethod
    def from_raw_response(cls, *, text, raw):
        self = cls()
        self.text = text
        self.raw = raw
        return self


class Conversation(SMBaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = []
    llm_model: Optional[str] = None
    llm_provider: Optional[str] = None

    def __str__(self):
        return f"<Conversation id={self.id!r}>"

    def add_message(self, role: str, text: str, meta: Dict[str, Any] = {}):
        """Add a new message to the conversation."""
        self.messages.append(Message(role=role, text=text, meta=meta))

    def send(
        self, llm_model: Optional[str] = None, llm_provider: Optional[str] = None
    ) -> Message:
        """Send the conversation to the LLM."""
        provider = find_provider(llm_provider or self.llm_provider)
        return provider.send_conversation(self)