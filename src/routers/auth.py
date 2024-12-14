from fastapi import APIRouter, Depends, status, Response
from src.controllers.auth_controller import AuthController
from src.services.user_service import UserService
from src.auth.token_manager import TokenManager
from src.schemas.user import UserCreate, UserLogin
from src.schemas.token import TokenData

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_controller() -> AuthController:
    return AuthController()


def get_user_service() -> UserService:
    return UserService()


def get_token_manager() -> TokenManager:
    return TokenManager()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    auth_controller: AuthController = Depends(get_auth_controller),
    user_service: UserService = Depends(get_user_service),
):
    return await auth_controller.register(user, user_service)


@router.post("/login")
async def login(
    response: Response,
    user_credentials: UserLogin,
    auth_controller: AuthController = Depends(get_auth_controller),
    user_service: UserService = Depends(get_user_service),
    token_manager: TokenManager = Depends(get_token_manager),
):
    return await auth_controller.login(
        response, user_credentials, user_service, token_manager
    )


@router.post("/logout")
async def logout(
    token: TokenData = Depends(get_token_manager().get_current_user),
    auth_controller: AuthController = Depends(get_auth_controller),
):

    return await auth_controller.logout(token)


@router.post("/refresh")
async def refresh(
    response: Response,
    token_manager: TokenManager = Depends(get_token_manager),
    auth_controller: AuthController = Depends(get_auth_controller),
):
    return await auth_controller.refresh_token(response, token_manager)
