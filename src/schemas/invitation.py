from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel

from src.schemas.study_room import StudyRoomListingOut
from src.schemas.user import UserInfo


class InvitationStatus(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class InvitationCreate(BaseModel):
    study_room_id: str
    invited_user_id: str


class InvitationListOut(BaseModel):
    id: str
    study_room_id: str
    invited_user_id: str
    inviter_user_id: str
    status: str
    created_at: datetime
    responded_at: Optional[datetime]
    inviter_user_info: UserInfo
    study_room_info: StudyRoomListingOut

    class Config:
        orm_mode = True
