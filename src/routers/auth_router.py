from fastapi import APIRouter, Depends, status, Response

from src.controllers.auth_controller import AuthController
from src.services.token_manager import TokenManager
from src.schemas.user import UserRegister, UserLogin
from src.schemas.token import TokenData

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_controller() -> AuthController:
    return AuthController()


def get_token_manager() -> TokenManager:
    return TokenManager()


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
    token_manager: TokenManager = Depends(get_token_manager),
    auth_controller: AuthController = Depends(get_auth_controller),
):
    return await auth_controller.login(
        user_data=user_data, response=response, token_manager=token_manager
    )


@router.post("/logout")
async def logout(
    token_data: tuple[TokenData, str] = Depends(get_token_manager().verify_token),
    auth_controller: AuthController = Depends(get_auth_controller),
):
    _, token = token_data
    return await auth_controller.logout(token=token)


@router.post("/refresh")
async def refresh(
    response: Response,
    token_manager: TokenManager = Depends(get_token_manager),
    auth_controller: AuthController = Depends(get_auth_controller),
):
    return await auth_controller.refresh_token(
        response=response, token_manager=token_manager
    )
