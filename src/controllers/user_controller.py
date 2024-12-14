from src.schemas.token import TokenData
from src.utils import create_response, convert_to_pydantic_object_id
from src.services.user_service import UserService
from src.constants import RESPONSE_STATUS_SUCCESS


class UserController:

    def __init__(self):
        self.user_service = UserService()

    async def search_users(self, query: str, token: TokenData):
        users = await self.user_service.search_users(query, token.user_id)
        return create_response(
            RESPONSE_STATUS_SUCCESS, "User fetched successfully", data={"users": users}
        )

    async def get_user_info(self, user_id: str):
        user = await self.user_service.get_user_by_id(
            convert_to_pydantic_object_id(user_id)
        )
        return create_response(
            RESPONSE_STATUS_SUCCESS, "User fetched successfully", data={"user": user}
        )

    async def get_user_friends(self, user_id: str):
        friends = await self.user_service.get_user_friends(user_id)
        return create_response(
            RESPONSE_STATUS_SUCCESS,
            "Friends fetched successfully",
            data={"friends": friends},
        )

    async def add_friend(self, user_id: str, friend_id: str):
        await self.user_service.add_friend(user_id, friend_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "Friend successfully added")

    async def remove_friend(self, user_id: str, friend_id: str):
        await self.user_service.remove_friend(user_id, friend_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "Friend successfully removed")
