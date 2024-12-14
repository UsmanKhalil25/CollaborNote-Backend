from typing import Optional
from pydantic import BaseModel, EmailStr
from src.documents.friend_request import FriendRequestStatus


class UserBase(BaseModel):
    id: str
    email: EmailStr


class UserCreate(UserBase):
    first_name: str
    last_name: str
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None


class UserSearch(UserBase):
    first_name: str
    last_name: str
    is_friend: bool
    friend_request_status: FriendRequestStatus


class UserLogin(UserBase):
    password: str


class UserInfo(BaseModel):
    email: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True
