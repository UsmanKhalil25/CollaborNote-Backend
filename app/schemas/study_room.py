from datetime import datetime
from typing import Optional,List
from pydantic import BaseModel, Field

from app.schemas.participant import  ParticipantOut



class StudyRoomCreate(BaseModel):
    name: str = Field(..., description="Name of the study room", max_length=100)
    description: Optional[str] = Field(None, description="Description of the study room", max_length=500)


class StudyRoomListingOut(BaseModel):
    id: str
    name: str
    description: str
    participants: List[ParticipantOut]
    created_at: datetime

    class Config:
        orm_mode = True

class StudyRoomDetailOut(StudyRoomListingOut):
    content: str
    is_active: bool
    created_at: datetime
    ended_at: Optional[datetime]

    class Config:
        orm_mode = True

class StudyRoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        orm_mode = True




