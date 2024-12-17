from fastapi import HTTPException, status
from typing import List

from src.documents.friend_request import FriendRequestStatus
from src.documents.user_document import User
from src.repositories.user_repository import UserRepository
from src.repositories.friend_request_repository import FriendRequestRepository
from src.schemas.user import UserSearch, UserInfo
from src.utils import validate_object_id, convert_to_pydantic_object_id


class UserService:

    def __init__(self):
        self.user_repository = UserRepository()
        self.friend_request_repository = FriendRequestRepository()

    async def get_valid_user(self, user_id: str) -> User:
        """Fetch and validate a user by ID."""
        validate_object_id(user_id)
        user_object_id = convert_to_pydantic_object_id(user_id)

        user = await self.user_repository.get_by_id(user_object_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        return user

    async def search_users(self, query: str, user_id: str) -> List[UserSearch]:
        """Fetch users by search query and include if they are friends and request status."""
        current_user = await self.get_valid_user(user_id)

        USER_SEARCH_QUERY = {
            "email": {"$regex": query, "$options": "i"},
            "_id": {"$ne": current_user.id},
        }
        users = await self.user_repository.search_by_query(USER_SEARCH_QUERY)

        if not users:
            return []

        friend_ids = set(current_user.friends)
        user_ids = [user.id for user in users]

        FRIEND_REQUEST_SEARCH_QUERY = {
            "sender_id": current_user.id,
            "receiver_id": {"$in": user_ids},
        }
        sent_requests = await self.friend_request_repository.search_by_query(
            FRIEND_REQUEST_SEARCH_QUERY
        )
        sent_requests_map = {
            request.receiver_id: request.status for request in sent_requests
        }

        return [
            UserSearch(
                id=str(user.id),
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_friend=str(user.id) in friend_ids,
                friend_request_status=sent_requests_map.get(
                    user.id, FriendRequestStatus.PENDING
                ),
            )
            for user in users
        ]

    async def get_user_friends(self, user_id: str) -> List[dict]:
        """Fetch a list of friends for a given User and return selected fields."""
        current_user = await self.get_valid_user(user_id)

        if not current_user.friends:
            return []

        FRIENDS_QUERY = {"_id": {"$in": current_user.friends}}

        friends = await self.user_repository.search_by_query(FRIENDS_QUERY)

        return [
            UserInfo(
                id=str(friend.id),
                email=friend.email,
                first_name=friend.first_name,
                last_name=friend.last_name,
            )
            for friend in friends
        ]

    @staticmethod
    async def update_friendship(user: User, friend: User, add: bool):
        """Add or remove a friend."""
        if add:
            user.friends.append(friend.id)
            friend.friends.append(user.id)
        else:
            user.friends.remove(friend.id)
            friend.friends.remove(user.id)

        await user.save()
        await friend.save()

    async def modify_friend(self, user_id: str, friend_id: str, add: bool):
        """Generalized method for adding or removing a friend."""
        action = "add" if add else "remove"
        if user_id == friend_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You cannot {action} yourself",
            )

        current_user = await self.get_valid_user(user_id)
        friend = await self.get_valid_user(friend_id)

        already_friends = friend.id in current_user.friends
        if add and already_friends:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already friends",
            )
        elif not add and not already_friends:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not friends with this user",
            )

        await self.update_friendship(current_user, friend, add)

    async def add_friend(self, user_id: str, friend_id: str):
        """Add a friend to the user's friend list."""
        await self.modify_friend(user_id, friend_id, add=True)

    async def remove_friend(self, user_id: str, friend_id: str):
        """Remove a friend from the user's friend list."""
        await self.modify_friend(user_id, friend_id, add=False)
