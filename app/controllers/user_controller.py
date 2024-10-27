from app.schemas import UserCreate, UserLogin
from app.services.user_service import UserService


class UserController:
    def __init__(self):
        self.user_service=UserService()

    async def register_user(self,user:UserCreate):
     
        await self.user_service.register_user(user=user)
        
    
    async def login_user(self,user_login:UserLogin):
        
        access_token=await self.user_service.login_user(user_login=user_login)
        return access_token
    

    async def make_token_blacklist(self,token:str):

        await self.user_service.make_token_blacklist(token=token)


