from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict


class Event(BaseModel):
    topic: str
    event_id: str
    timestamp: datetime
    source: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class PublishBatch(BaseModel):
    __root__: list[Event]