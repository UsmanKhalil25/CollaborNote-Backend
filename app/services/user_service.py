from fastapi import HTTPException,status
from pydantic import EmailStr
from app.models.blacklist_token import BlackListToken
from app.models.user import User
from app.schemas import UserCreate, UserLogin
from app.secutiry import create_access_token
from app.utils import hash_password, verify_password


class UserService:

    async def get_user(self,user_email:EmailStr):
        return await User.find_one({"email":user_email})
    

    async def register_user(self,user:UserCreate):

        existing_user=await self.get_user(user_email=user.email)
        if existing_user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Email already registered")
    
        hashed_password=hash_password(password=user.password)

        new_user=User(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            password=hashed_password,
        )

        await new_user.insert()
        
    async def login_user(self,user_login:UserLogin):
         
        existing_user=await self.get_user(user_email=user_login.email)
        if existing_user is None or verify_password(plain_password=user_login.password,
                           hashed_password=existing_user.password) is False: 
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Invalid credentials")
        
        access_token=create_access_token(data={
            "user_id":str(existing_user.id)
        })

        return access_token

    async def make_token_blacklist(self,token:str):
        blacklits_token=BlackListToken(
            token=token
        )

        await blacklits_token.insert()
