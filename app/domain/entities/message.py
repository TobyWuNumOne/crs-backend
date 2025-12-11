"""Message entity placeholder."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    id: int
    to_user_id: int
    content: str
    created_at: datetime
