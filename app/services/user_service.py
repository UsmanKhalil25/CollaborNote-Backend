from fastapi import HTTPException, status
from typing import List
from beanie import PydanticObjectId
from pydantic import EmailStr
from app.models.user import User
from app.utils import validate_object_id, convert_to_pydantic_object_id

class UserService:

    @staticmethod
    async def get_user_by_id(user_id: PydanticObjectId) -> User:
        """Fetch a user by user ID, raises HTTPException if not found."""

        user = await User.find_one({"_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not exist"
            )
        return user


    @staticmethod
    async def get_user_by_email(user_email: EmailStr) -> User | None:
        """Fetch a user by email."""
        return await User.find_one({"email": user_email})


    async def get_user_friends(self, user_id: str) -> List[User]:
        """Fetch a list of friends for a given user."""
        validate_object_id(user_id)
        user_object_id = convert_to_pydantic_object_id(user_id)
        user = await self.get_user_by_id(user_object_id)
        friends = await User.find({"_id": {"$in": user.friends}}).to_list()
        return friends


    @staticmethod
    async def update_friendship(user: User, friend: User, add: bool):
        if add:
            user.friends.append(friend.id)
            friend.friends.append(user.id)
        else:
            user.friends.remove(friend.id)
            friend.friends.remove(user.id)

        # Save both users concurrently for efficiency
        await user.save()
        await friend.save()


    @staticmethod
    def check_if_already_friends( user: User, friend_object_id: PydanticObjectId) -> bool:
        """Check if two users are already friends."""
        return friend_object_id in user.friends


    async def add_friend(self, user_id: str, friend_id: str):
        """Add a friend to a user's friend list."""

        validate_object_id(user_id)
        validate_object_id(friend_id)

        if user_id == friend_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot add yourself as a friend"
            )

        user_object_id = convert_to_pydantic_object_id(user_id)
        friend_object_id = convert_to_pydantic_object_id(friend_id)

        user = await self.get_user_by_id(user_object_id)
        friend = await self.get_user_by_id(friend_object_id)

        if self.check_if_already_friends(user, friend_object_id):
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already friends"
            )

        await self.update_friendship(user, friend, add=True)


    async def remove_friend(self, user_id: str, friend_id: str):
        """Remove a friend from a user's friend list."""
                
        validate_object_id(user_id)
        validate_object_id(friend_id)

        if user_id == friend_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot remove yourself from your friend list"
            )

        user_object_id = convert_to_pydantic_object_id(user_id)
        friend_object_id = convert_to_pydantic_object_id(friend_id)

        user = await self.get_user_by_id(user_object_id)
        friend = await self.get_user_by_id(friend_object_id)

        if not self.check_if_already_friends(user, friend_object_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not friends with this user"
            )

        await self.update_friendship(user,friend, add=False)


