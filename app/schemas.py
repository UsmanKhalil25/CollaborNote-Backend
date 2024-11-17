from datetime import datetime
from typing import Optional,List
from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr, model_validator

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    first_name: str 
    last_name: str 
    password: str 


class UserLogin(UserBase):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str


class Participant(BaseModel):
    participant_id: str
    can_edit: bool


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