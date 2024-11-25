from pydantic import BaseModel, EmailStr, Field
from beanie import PydanticObjectId
from enum import Enum


class Permission(str, Enum):
    can_edit = "can_edit"
    can_view = "can_view"


class Participant(BaseModel):
    user_id: PydanticObjectId
    is_owner: bool = False
    is_active: bool = False
    permission: Permission = Permission.can_view

class ParticipantOut(Participant):
    email: EmailStr
    first_name: str
    last_name: str


class ParticipantCreate(BaseModel):
    user_id: PydanticObjectId = Field(..., description="ID of the user")
    is_owner: bool = False
    is_active: bool =  True
    permission: Permission = Permission.can_view
