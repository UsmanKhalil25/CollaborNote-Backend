from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    first_name: str 
    last_name: str 
    password: str 


class UserLogin(UserBase):
    password: str

class UserInfo(BaseModel):
    email: str
    first_name: str
    last_name: str
        
    class Config:
        orm_mode = True