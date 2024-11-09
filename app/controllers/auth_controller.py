from fastapi import HTTPException, status
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.schemas import UserCreate, UserLogin
from app.utils import create_response

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()

    async def register(self, user: UserCreate, user_service: UserService):
        try:
            await self.auth_service.register(user, user_service)
            return create_response("success", "User registered successfully")
        except HTTPException as e:
            raise e

    async def login(self, user_login: UserLogin, user_service: UserService):
        try:
            access_token = await self.auth_service.login(user_login, user_service)
            return create_response("success", "Login successful", data={"access_token": access_token})
        except HTTPException as e:
            raise e

    async def logout(self, token: str):
        try:
            await self.auth_service.blacklist_token(token)
            return create_response("success", "Logout successful")
        except HTTPException as e:
            raise e
