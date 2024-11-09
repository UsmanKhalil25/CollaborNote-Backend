from typing import List
from pydantic import EmailStr
from bson import ObjectId
from fastapi import HTTPException, status
from app.models.user import User


class UserService:

    def _convert_to_object_id(self, user_id: str) -> ObjectId:
        """Convert a string user ID to an ObjectId."""
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        return ObjectId(user_id)
        
    async def _get_user_by_id(self, user_id: ObjectId) -> User:
        """Fetch a user by user ID, raises HTTPException if not found."""

        user = await User.find_one({"_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not exist"
            )
        return user

    async def get_user_by_email(self, user_email: EmailStr) -> User | None:
        """Fetch a user by email."""
        
        return await User.find_one({"email": user_email})

    async def get_user_friends(self, user_id: str) -> List[User]:
        """Fetch a list of friends for a given user."""
        
        user = await self._get_user_by_id(self._convert_to_object_id(user_id))
        friends = await User.find({"_id": {"$in": user.friends}}).to_list()
        return friends

    async def _check_if_already_friends(self, user: User, friend_id: str):
        """Check if two users are already friends."""

        if self._convert_to_object_id(friend_id) in user.friends:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already friends"
            )
        
    async def add_friend(self, user_id: str, friend_id: str):
        """Add a friend to a user's friend list."""
        
        if user_id == friend_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot add yourself as a friend"
            )

        user = await self._get_user_by_id(self._convert_to_object_id(user_id))
        friend = await self._get_user_by_id(self._convert_to_object_id(friend_id))

        await self._check_if_already_friends(user, friend_id)

        user.friends.append(friend_id)
        await user.save()

        friend.friends.append(user_id)
        await friend.save()

    async def remove_friend(self, user_id: str, friend_id: str):
        """Remove a friend from a user's friend list."""
        
        if user_id == friend_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot remove yourself from your friend list"
            )

        user = await self._get_user_by_id(self._convert_to_object_id(user_id))
        friend = await self._get_user_by_id(self._convert_to_object_id(friend_id))

        if self._convert_to_object_id(friend_id) not in user.friends:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not friends with this user"
            )

        user.friends.remove(self._convert_to_object_id(friend_id))
        await user.save()

        friend.friends.remove(self._convert_to_object_id(user_id))
        await friend.save()


