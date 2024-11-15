from app.utils import create_response
from app.services.user_service import UserService
from app.constants import RESPONSE_STATUS_SUCCESS

class UserController:
    def __init__(self):
        self.user_service = UserService()

    async def get_user_friends(self, user_id: str):
        friends = await self.user_service.get_user_friends(user_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "Friends fetched successfully", data={"friends":friends})
    
    async def add_friend(self, user_id: str, friend_id: str):
        await self.user_service.add_friend(user_id, friend_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "Friend successfully added")

    async def remove_friend(self, user_id: str, friend_id: str):
        await self.user_service.remove_friend(user_id, friend_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "Friend successfully removed")