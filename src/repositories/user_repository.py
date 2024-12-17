from typing import List, Optional
from beanie import PydanticObjectId

from src.documents.user_document import User
from src.schemas.user import UserUpdate


class UserRepository:
    @staticmethod
    async def search_by_query(query: dict) -> List[User]:
        """Search for users based on a query dictionary."""

        users = await User.find(query).to_list()
        return users

    @staticmethod
    async def get_by_email(email: str) -> Optional[User]:
        """Retrieve a user document by their email address."""

        return await User.find_one(User.email == email)

    @staticmethod
    async def get_by_id(id: PydanticObjectId) -> Optional[User]:
        """Retrieve a user document by their ID."""

        return await User.get(id)

    @staticmethod
    async def create(user_data: dict) -> User:
        """Create a new user document and save it to the database."""
        user = User(**user_data)
        await user.insert()
        return user

    async def update(
        self, id: PydanticObjectId, user_data: UserUpdate
    ) -> Optional[User]:
        """Update an existing user document with new data."""
        user = await self.get_by_id(id)

        for field, value in user_data.model_dump().items():
            if value is not None:
                setattr(user, field, value)
        await user.save()
        return user

    async def delete(self, id: PydanticObjectId) -> Optional[Exception]:
        """Delete a user document by their ID."""

        user, error = await self.ensure_user_exists(id)
        if error:
            return error

        await user.delete()
