from beanie import Document, Indexed
from pydantic import EmailStr

class User(Document):
    email: EmailStr
    first_name: str
    last_name: str
    password: str

    class Settings:
        collection = "users"
