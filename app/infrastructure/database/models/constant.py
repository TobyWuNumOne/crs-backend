from enum import Enum


class Role(str, Enum):
    doctor = "doctor"
    patient = "patient"
    admin = "admin"


class Sex(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class TimeSlot(str, Enum):
    morning = "morning"  # 上午
    afternoon = "afternoon"  # 下午
    evening = "evening"  # 夜間


class RegistrationStatus(str, Enum):
    registered = "registered"
    cancelled = "cancelled"
    completed = "completed"
    no_show = "no_show"
