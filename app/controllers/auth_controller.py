from fastapi import HTTPException, status
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.schemas import UserCreate, UserLogin
from app.utils import create_response
from app.constants import RESPONSE_STATUS_SUCCESS

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()

    async def register(self, user: UserCreate, user_service: UserService):
        await self.auth_service.register(user, user_service)
        return create_response(RESPONSE_STATUS_SUCCESS, "User registered successfully")

    async def login(self, user_login: UserLogin, user_service: UserService):
        access_token = await self.auth_service.login(user_login, user_service)
        return create_response(RESPONSE_STATUS_SUCCESS, "Login successfull", data={"access_token": access_token})

    async def logout(self, token: str):
        await self.auth_service.blacklist_token(token)
        return create_response(RESPONSE_STATUS_SUCCESS, "Logout successfull")
