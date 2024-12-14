from typing import List, Optional, Annotated
from beanie import PydanticObjectId, Indexed
from pydantic import EmailStr
from .base_document import BaseDocument


class UserDocument(BaseDocument):
    email: EmailStr = Annotated[EmailStr, Indexed(unique=True, text=True)]
    first_name: str
    last_name: str
    password: str
    friends: Optional[List[PydanticObjectId]] = None
    friend_requests_sent: Optional[List[PydanticObjectId]] = None
    friend_requests_received: Optional[List[PydanticObjectId]] = None

    class Settings:
        collection = "users"
