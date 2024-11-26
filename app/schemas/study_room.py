from datetime import datetime
from typing import Optional,List
from pydantic import BaseModel, Field, model_validator

from app.schemas.participant import Participant, ParticipantOut



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


class StudyRoomOut(BaseModel):
    id:str
    name: str
    description: Optional[str]
    owner_id: str
    active_participants: List[Participant] = []  # List of dictionaries containing participant details
    former_participants: List[str] = []
    created_at: datetime = datetime.now()
    is_active: bool = True
    markdown_content: str
    last_modified: datetime = datetime.now()

    class Config:
        from_attributes = True



class StudyRoomCreate(BaseModel):
    name:str
    description:Optional[str]=None


class StudyRoomInfoUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @model_validator(mode='before')
    def check_at_least_one_field(cls, values):
        name = values.get('name')
        description = values.get('description')

        # Ensure that at least one of 'name' or 'description' is provided
        if not name and not description:
            raise ValueError('At least one of "name" or "description" must be provided.')

        return values
    

class MarkDownData(BaseModel):
    markdown_data:str