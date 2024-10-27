from pydantic import EmailStr
from app.models.blackListToken import BlackListToken
from app.models.user import User
from app.schemas import UserCreate
from app.utils import hash_password


class UserService:

    async def get_user(self,user_email:EmailStr):
        return await User.find_one({"email":user_email})
    

    async def register_user(self,user:UserCreate):
        hashed_password=hash_password(password=user.password)

        new_user=User(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            password=hashed_password,
        )

        await new_user.insert()
        

    async def make_token_blacklist(self,token:str):
        blacklits_token=BlackListToken(
            token=token
        )

        await blacklits_token.insert()
