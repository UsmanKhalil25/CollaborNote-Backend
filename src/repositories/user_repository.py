from typing import List, Optional
from beanie import PydanticObjectId

from src.documents.user_document import UserDocument
from src.schemas.user import UserCreate, UserUpdate


class UserRepository:
    @staticmethod
    async def search_by_query(query: dict) -> List[UserDocument]:
        """Search for users based on a query dictionary."""

        users = await UserDocument.find(query).to_list()
        return users

    @staticmethod
    async def get_by_email(email: str) -> Optional[UserDocument]:
        """Retrieve a user document by their email address."""

        return await UserDocument.find_one(email=email)

    @staticmethod
    async def get_by_id(id: PydanticObjectId) -> Optional[UserDocument]:
        """Retrieve a user document by their ID."""

        return await UserDocument.get(id)

    @staticmethod
    async def create(user_data: UserCreate):
        """Create a new user document and save it to the database."""

        user = UserDocument(**user_data.model_dump())
        await user.save()
        return user

    async def update(
        self, id: PydanticObjectId, user_data: UserUpdate
    ) -> Optional[UserDocument]:
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
