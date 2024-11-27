from enum import Enum
from pydantic import BaseModel

class InvitationStatus(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class InvitationCreate(BaseModel):
    study_room_id: str
    invited_user_id: str
    