from fastapi import APIRouter, Depends, status
from src.controllers.user_controller import UserController
from src.auth.token_manager import TokenManager
from src.schemas.token import TokenData

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_controller() -> UserController:
    return UserController()


def get_token_manager() -> TokenManager:
    return TokenManager()


@router.get("/search")
async def search_users(
    query: str,
    token: TokenData = Depends(get_token_manager().verify_token),
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.search_users(query, token)


@router.get("/current")
async def get_user_info(
    token: TokenData = Depends(get_token_manager().get_current_user),
    user_controller: UserController = Depends(get_user_controller),
):
    user_id = token.id
    return await user_controller.get_user_info(user_id)


@router.get("/friends")
async def get_user_friends(
    token: TokenData = Depends(get_token_manager().get_current_user),
    user_controller: UserController = Depends(get_user_controller),
):
    user_id = token.id
    return await user_controller.get_user_friends(user_id)


@router.post("/friends/{friend_id}", status_code=status.HTTP_201_CREATED)
async def add_friend(
    friend_id: str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    user_controller: UserController = Depends(get_user_controller),
):
    user_id = token.id
    return await user_controller.add_friend(user_id, friend_id)


@router.delete("/friends/{friend_id}")
async def remove_friend(
    friend_id: str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    user_controller: UserController = Depends(get_user_controller),
):
    user_id = token.id
    return await user_controller.remove_friend(user_id, friend_id)
