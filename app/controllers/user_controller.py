from fastapi import HTTPException, status
from app.services.user_service import UserService
from app.schemas import UserCreate, UserLogin
from app.utils import create_response

class UserController:
    def __init__(self):
        self.user_service = UserService()

    async def register_user(self, user: UserCreate):
        try:
            await self.user_service.register_user(user)
            return create_response("success", "User registered successfully")
        except HTTPException as e:
            raise e

    async def login_user(self, user_login: UserLogin):
        try:
            access_token = await self.user_service.login_user(user_login)
            return create_response("success", "Login successful", data={"access_token": access_token})
        except HTTPException as e:
            raise e

    async def logout_user(self, token: str):
        try:
            await self.user_service.make_token_blacklist(token)
            return create_response("success", "Logout successful")
        except HTTPException as e:
            raise e
