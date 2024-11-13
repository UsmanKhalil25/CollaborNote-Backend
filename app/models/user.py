from beanie import Document, PydanticObjectId
from pydantic import EmailStr
from typing import List

class User(Document):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    friends: List[PydanticObjectId] = []  
    friend_requests_sent: List[PydanticObjectId] = []  
    friend_requests_received: List[PydanticObjectId] = []  

    class Settings:
        collection = "users"
