from typing import List, Optional, Annotated
from beanie import PydanticObjectId, Indexed
from pydantic import EmailStr
from .base_document import BaseDocument


class User(BaseDocument):
    email: EmailStr = Annotated[EmailStr, Indexed(unique=True, text=True)]
    first_name: str
    last_name: str
    password: str
    friends: List[PydanticObjectId] = []
    friend_requests_sent: List[PydanticObjectId] = []
    friend_requests_received: List[PydanticObjectId] = []

    class Settings:
        collection = "users"
