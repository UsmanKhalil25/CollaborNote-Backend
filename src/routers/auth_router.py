from fastapi import APIRouter, Depends, status, Response

from src.controllers.auth_controller import AuthController
from src.services.token_service import TokenService
from src.schemas.user import UserRegister, UserLogin
from src.schemas.token import TokenData

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_controller() -> AuthController:
    """Provides a AuthController instance."""

    return AuthController()


def get_token_service() -> TokenService:
    """Provides a TokenService instance."""

    return TokenService()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    auth_controller: AuthController = Depends(get_auth_controller),
):
    return await auth_controller.register(user_data)


@router.post("/login")
async def login(
    user_data: UserLogin,
    response: Response,
    auth_controller: AuthController = Depends(get_auth_controller),
):
    return await auth_controller.login(user_data=user_data, response=response)


@router.post("/logout")
async def logout(
    token_data: TokenData = Depends(get_token_service().validate_access_token),
    auth_controller: AuthController = Depends(get_auth_controller),
):
    return await auth_controller.logout(token=token_data.token)


@router.post("/refresh")
async def refresh(
    response: Response,
    auth_controller: AuthController = Depends(get_auth_controller),
):
    return await auth_controller.refresh_token(response=response)
