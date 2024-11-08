from fastapi import APIRouter, Depends, status
from app.controllers.user_controller import UserController
from app.schemas import UserCreate, UserLogin

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

def get_user_controller() -> UserController:
    return UserController()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    user_controller: UserController = Depends(get_user_controller)
):
    return await user_controller.register_user(user)

@router.post("/login")
async def login(
    user_credentials: UserLogin,
    user_controller: UserController = Depends(get_user_controller)
):
    return await user_controller.login_user(user_credentials)

@router.post("/logout")
async def logout(
    token: str,
    user_controller: UserController = Depends(get_user_controller)
):
    return await user_controller.logout_user(token)
