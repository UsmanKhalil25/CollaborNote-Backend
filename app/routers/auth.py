from fastapi import APIRouter, Depends, HTTPException, status, Response, Header
from app.auth import token_manager
from app.controllers.auth_controller import AuthController
from app.services.user_service import UserService
from app.auth.token_manager import TokenManager
from app.schemas import UserCreate, UserLogin

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

def get_auth_controller() -> AuthController:
    return AuthController()

def get_user_service() -> UserService:
    return UserService()

def get_token_manager()->TokenManager:
    return TokenManager()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    auth_controller: AuthController = Depends(get_auth_controller),
    user_service: UserService = Depends(get_user_service)

):
    return await auth_controller.register(user, user_service)

@router.post("/login")
async def login(
    response: Response,
    user_credentials: UserLogin,
    auth_controller: AuthController = Depends(get_auth_controller),
    user_service: UserService = Depends(get_user_service),
    token_manager: TokenManager = Depends(get_token_manager)
):
    return await auth_controller.login(response, user_credentials, user_service, token_manager)

@router.post("/logout")
async def logout(
    authorization: str = Header(...),  
    auth_controller: AuthController = Depends(get_auth_controller)
):
    token = authorization.split(" ")[1] 
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token missing or malformed"
        )
    return await auth_controller.logout(token)


@router.post("/refresh")
async def refresh(
        response: Response,
        token_manager: TokenManager = Depends(get_token_manager),
        auth_controller: AuthController = Depends(get_auth_controller)
):
    return await auth_controller.refresh_token(response, token_manager)


