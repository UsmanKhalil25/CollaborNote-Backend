from src.schemas.token import TokenData
from src.utils import create_response
from src.services.user_service import UserService
from src.constants import RESPONSE_STATUS_SUCCESS


class UserController:

    def __init__(self):
        self.user_service = UserService()

    async def search_users(self, query: str, token: TokenData):
        user_id = token.user_id
        users = await self.user_service.search_users(query=query, user_id=user_id)
        return create_response(
            RESPONSE_STATUS_SUCCESS, "User fetched successfully", data={"users": users}
        )

    async def get_current_user(self, token: TokenData):
        user_id = token.user_id
        current_user = await self.user_service.get_valid_user(user_id=user_id)
        return create_response(
            RESPONSE_STATUS_SUCCESS,
            "Current user fetched successfully",
            data={"current_user": current_user},
        )

    async def get_user_friends(self, token: TokenData):
        user_id = token.user_id
        friends = await self.user_service.get_user_friends(user_id=user_id)
        return create_response(
            RESPONSE_STATUS_SUCCESS,
            "Friends fetched successfully",
            data={"friends": friends},
        )

    async def add_friend(self, friend_id: str, token: TokenData):
        user_id = token.user_id
        await self.user_service.add_friend(friend_id=friend_id, user_id=user_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "Friend successfully added")

    async def remove_friend(self, friend_id: str, token: TokenData):
        user_id = token.user_id
        await self.user_service.remove_friend(friend_id=friend_id, user_id=user_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "Friend successfully removed")
