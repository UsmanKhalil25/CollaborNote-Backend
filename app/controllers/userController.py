from fastapi import HTTPException,status
from app.schemas import UserCreate, UserLogin
from app.secutiry import create_access_token
from app.services.userService import UserService
from app.utils import verify_password


class UserController:
    def __init__(self):
        self.user_service=UserService()

    async def register_user(self,user:UserCreate):
        
        existing_user=await self.user_service.get_user(user_email=user.email)
        if existing_user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Email already registered")
        
        await self.user_service.register_user(user=user)
        
    
    async def login_user(self,user_login:UserLogin):
        existing_user=await self.user_service.get_user(user_email=user_login.email)
        if existing_user is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Invalid credentials")
        
        if verify_password(plain_password=user_login.password,
                           hashed_password=existing_user.password) is False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Invalid credentials")
        
        access_token=create_access_token(data={
            "user_id":str(existing_user.id)
        })

        return access_token
    

    async def make_token_blacklist(self,token:str):
        #check in verify token function for token is in blacklist-token or not
        await self.user_service.make_token_blacklist(token=token)


