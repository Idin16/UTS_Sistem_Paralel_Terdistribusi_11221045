from typing import Any, Dict, List
from pydantic import BaseModel, Field, validator
from datetime import datetime

class Event(BaseModel):
    topic: str = Field(..., min_length=1)
    event_id: str = Field(..., min_length=1)
    timestamp: str
    source: str = Field(..., min_length=1)
    payload: Dict[str, Any]

    @validator("timestamp")
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v)
        except Exception:
            raise ValueError("timestamp must be in ISO8601 format")
        return v


class Stats(BaseModel):
    received: int
    unique_processed: int
    duplicate_dropped: int
    topics: List[str]
    uptime_seconds: float
