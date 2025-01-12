from fastapi import Response

from src.services.auth_service import AuthService
from src.schemas.user import UserRegister, UserLogin
from src.utils import create_response
from src.constants import RESPONSE_STATUS_SUCCESS


class AuthController:
    """Controller for handling authentication-related operations."""

    def __init__(self):
        self.auth_service = AuthService()

    async def register(self, user_data: UserRegister):
        """Register a new user."""

        await self.auth_service.register(user_data=user_data)
        return create_response(RESPONSE_STATUS_SUCCESS, "User registered successfully")

    async def login(
        self,
        user_data: UserLogin,
        response: Response,
    ):
        """Authenticate a user and return an access token."""

        access_token = await self.auth_service.login(
            user_data=user_data, response=response
        )
        return create_response(
            RESPONSE_STATUS_SUCCESS,
            "Login successful",
            data={"access_token": access_token},
        )

    async def refresh_token(self, response: Response):
        """Refresh the access token using the refresh token."""

        new_access_token = await self.auth_service.refresh_token(response=response)
        return create_response(
            RESPONSE_STATUS_SUCCESS,
            "Token refreshed successfully",
            data={"access_token": new_access_token},
        )

    async def logout(self, token: str):
        """Log out a user by blacklisting the provided token."""

        await self.auth_service.blacklist_token(token=token)
        return create_response(RESPONSE_STATUS_SUCCESS, "Logged out successfully")
