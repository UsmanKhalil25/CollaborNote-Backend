from fastapi import APIRouter, Depends, status
from app.controllers.user_controller import UserController

router = APIRouter(
    prefix="/users",
     tags=["Users"]
)

def get_user_controller() -> UserController:
    return UserController()


@router.get("/{user_id}/friends")
async def get_user_friends(
    user_id: str,
    user_controller: UserController =  Depends(get_user_controller)
):
    return await user_controller.get_user_friends(user_id)

@router.post("/{user_id}/friends/{friend_id}",  status_code=status.HTTP_201_CREATED)
async def add_friend(
    user_id: str,
    friend_id: str,
    user_controller: UserController =  Depends(get_user_controller)
):
    return await user_controller.add_friend(user_id, friend_id)


@router.delete("/{user_id}/friends/{friend_id}")
async def remove_friend(
    user_id: str,
    friend_id: str,
    user_controller: UserController = Depends(get_user_controller)
):
    return await user_controller.remove_friend(user_id, friend_id)

