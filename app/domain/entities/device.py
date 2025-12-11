"""Device entity placeholder."""

from dataclasses import dataclass


@dataclass
class Device:
    id: int
    owner_id: int
    token: str
