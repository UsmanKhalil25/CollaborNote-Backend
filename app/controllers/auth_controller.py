from fastapi import Response
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserLogin
from app.utils import create_response
from app.constants import RESPONSE_STATUS_SUCCESS
from app.auth.token_manager import  TokenManager

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()

    async def register(self, user: UserCreate, user_service: UserService):
        await self.auth_service.register(user, user_service)
        return create_response(RESPONSE_STATUS_SUCCESS, "User registered successfully")

    async def login(self,response: Response, user_login: UserLogin, user_service: UserService, token_manager: TokenManager):
        access_token = await self.auth_service.login(response, user_login, user_service, token_manager)
        return create_response(RESPONSE_STATUS_SUCCESS, "Login successful", data={"access_token": access_token})

    async def logout(self, token: str):
        await self.auth_service.blacklist_token(token)
        return create_response(RESPONSE_STATUS_SUCCESS, "Logout successful")

    async def refresh_token(self, response: Response, token_manager: TokenManager):
        return await self.auth_service.refresh_token(response, token_manager)