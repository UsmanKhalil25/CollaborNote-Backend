from fastapi import APIRouter, Depends, HTTPException, Header, status
from app.controllers.auth_controller import AuthController
from app.services.user_service import UserService
from app.schemas import UserCreate, UserLogin

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

def get_auth_controller() -> AuthController:
    return AuthController()

def get_user_service() -> UserService:
    return UserService()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    auth_controller: AuthController = Depends(get_auth_controller),
    user_service: UserService = Depends(get_user_service)

):
    return await auth_controller.register(user, user_service)

@router.post("/login")
async def login(
    user_credentials: UserLogin,
    auth_controller: AuthController = Depends(get_auth_controller),
    user_service: UserService = Depends(get_user_service)
):
    return await auth_controller.login(user_credentials, user_service)

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