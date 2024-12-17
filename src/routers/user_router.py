from fastapi import APIRouter, Depends, status

from src.controllers.user_controller import UserController
from src.services.token_manager import TokenManager
from src.schemas.token import TokenData

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_controller() -> UserController:
    return UserController()


def get_token_manager() -> TokenManager:
    return TokenManager()


@router.get("/search")
async def search_users(
    query: str,
    token_data: tuple[TokenData, str] = Depends(get_token_manager().verify_token),
    user_controller: UserController = Depends(get_user_controller),
):
    token, _ = token_data
    return await user_controller.search_users(query=query, token=token)


@router.get("/current")
async def get_user_info(
    token_data: tuple[TokenData, str] = Depends(get_token_manager().verify_token),
    user_controller: UserController = Depends(get_user_controller),
):
    token, _ = token_data
    return await user_controller.get_current_user(token=token)


@router.get("/friends")
async def get_user_friends(
    token_data: tuple[TokenData, str] = Depends(get_token_manager().verify_token),
    user_controller: UserController = Depends(get_user_controller),
):
    token, _ = token_data
    return await user_controller.get_user_friends(token=token)


@router.post("/friends/{friend_id}", status_code=status.HTTP_201_CREATED)
async def add_friend(
    friend_id: str,
    token_data: tuple[TokenData, str] = Depends(get_token_manager().verify_token),
    user_controller: UserController = Depends(get_user_controller),
):
    token, _ = token_data
    return await user_controller.add_friend(friend_id=friend_id, token=token)


@router.delete("/friends/{friend_id}")
async def remove_friend(
    friend_id: str,
    token_data: tuple[TokenData, str] = Depends(get_token_manager().verify_token),
    user_controller: UserController = Depends(get_user_controller),
):
    token, _ = token_data
    return await user_controller.remove_friend(friend_id=friend_id, token=token)
