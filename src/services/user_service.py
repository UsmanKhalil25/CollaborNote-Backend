from fastapi import HTTPException, status
from typing import List
from beanie import PydanticObjectId
from pydantic import EmailStr

from src.documents.friend_request import FriendRequestStatus
from src.documents.user_document import UserDocument
from src.repositories.user_repository import UserRepository
from src.repositories.friend_request_repository import FriendRequestRepository
from src.schemas.user import UserSearch
from src.utils import validate_object_id, convert_to_pydantic_object_id


class UserService:

    def __init__(self):
        self.user_repository = UserRepository()
        self.friend_request_repository = FriendRequestRepository()

    async def search_users(self, query: str, user_id: str) -> List[UserSearch]:
        """Fetch users by search query and include if they are friends with the current user and the friend request status"""

        validate_object_id(user_id)
        user_object_id = convert_to_pydantic_object_id(user_id)

        USER_SEARCH_QUERY = {
            "email": {"$regex": query, "$options": "i"},
            "_id": {"$ne": user_object_id},
        }
        users = await self.user_repository.search_by_query(USER_SEARCH_QUERY)
        if not users:
            return []

        current_user = await self.user_repository.get_by_id(user_object_id)
        friend_ids = set(current_user.friends)

        user_ids = [user.id for user in users]

        FRIEND_REQUEST_SEARCH_QUERY = {
            "sender_id": user_object_id,
            "receiver_id": {"$in": user_ids},
        }
        sent_requests = await self.friend_request_repository.search_by_query(
            FRIEND_REQUEST_SEARCH_QUERY
        )
        sent_requests_map = {
            request.receiver_id: request.status for request in sent_requests
        }

        user_search_results = [
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

        return user_search_results

    @staticmethod
    async def get_user_by_id(user_id: PydanticObjectId) -> UserDocument:
        """Fetch a user by user ID, raises HTTPException if not found."""

        user = await UserDocument.find_one({"_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist"
            )
        return user

    @staticmethod
    async def get_user_by_email(user_email: EmailStr) -> UserDocument | None:
        """Fetch a user by email."""
        return await UserDocument.find_one({"email": user_email})

    async def get_user_friends(self, user_id: str) -> List[UserDocument]:
        """Fetch a list of friends for a given UserDocument."""
        validate_object_id(user_id)
        user_object_id = convert_to_pydantic_object_id(user_id)
        user = await self.get_user_by_id(user_object_id)
        friends = await UserDocument.find(
            {"_id": {"$in": UserDocument.friends}}
        ).to_list()
        return friends

    @staticmethod
    async def update_friendship(user: UserDocument, friend: UserDocument, add: bool):
        if add:
            UserDocument.friends.append(friend.id)
            friend.friends.append(UserDocument.id)
        else:
            UserDocument.friends.remove(friend.id)
            friend.friends.remove(UserDocument.id)

        await UserDocument.save()
        await friend.save()

    @staticmethod
    def check_if_already_friends(
        user: UserDocument, friend_object_id: PydanticObjectId
    ) -> bool:
        """Check if two users are already friends."""
        return friend_object_id in UserDocument.friends

    async def add_friend(self, user_id: str, friend_id: str):
        """Add a friend to a user's friend list."""

        validate_object_id(user_id)
        validate_object_id(friend_id)

        if user_id == friend_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot add yourself as a friend",
            )

        user_object_id = convert_to_pydantic_object_id(user_id)
        friend_object_id = convert_to_pydantic_object_id(friend_id)

        user = await self.get_user_by_id(user_object_id)
        friend = await self.get_user_by_id(friend_object_id)

        if self.check_if_already_friends(user, friend_object_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already friends",
            )

        await self.update_friendship(user, friend, add=True)

    async def remove_friend(self, user_id: str, friend_id: str):
        """Remove a friend from a user's friend list."""

        validate_object_id(user_id)
        validate_object_id(friend_id)

        if user_id == friend_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot remove yourself from your friend list",
            )

        user_object_id = convert_to_pydantic_object_id(user_id)
        friend_object_id = convert_to_pydantic_object_id(friend_id)

        user = await self.get_user_by_id(user_object_id)
        friend = await self.get_user_by_id(friend_object_id)

        if not self.check_if_already_friends(user, friend_object_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not friends with this user",
            )

        await self.update_friendship(user, friend, add=False)
