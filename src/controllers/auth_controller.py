from fastapi import Response

from src.services.auth_service import AuthService
from src.schemas.user import UserRegister, UserLogin
from src.utils import create_response
from src.constants import RESPONSE_STATUS_SUCCESS
from src.services.token_manager import TokenManager


class AuthController:
    def __init__(self):
        self.auth_service = AuthService()

    async def register(self, user_data: UserRegister):
        await self.auth_service.register(user_data)
        return create_response(RESPONSE_STATUS_SUCCESS, "User registered successfully")

    async def login(
        self,
        user_data: UserLogin,
        response: Response,
        token_manager: TokenManager,
    ):
        access_token = await self.auth_service.login(
            user_data=user_data, response=response, token_manager=token_manager
        )
        return create_response(
            RESPONSE_STATUS_SUCCESS,
            "Login successful",
            data={"access_token": access_token},
        )

    async def refresh_token(self, response: Response, token_manager: TokenManager):
        new_access_token = await self.auth_service.refresh_token(
            response, token_manager
        )
        return create_response(
            RESPONSE_STATUS_SUCCESS,
            "Token refreshed successfully",
            data={"access_token": new_access_token},
        )

    async def logout(self, token: str):
        await self.auth_service.blacklist_token(token)
        return create_response(RESPONSE_STATUS_SUCCESS, "Logged out successfully")
