"""Example domain entity: Item (generic example)

Replace with domain types: Doctor, Patient, Clinic, Registration when implementing.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Item:
    id: int
    name: str
    created_at: datetime
