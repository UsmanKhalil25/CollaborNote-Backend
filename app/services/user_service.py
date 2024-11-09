from pydantic import EmailStr
from app.models.user import User

class UserService:
    async def get_user_by_id(self, user_id: str) -> User | None:
        """Fetch a user by user ID."""
        return await User.find_one({"_id": user_id})
    
    async def get_user_by_email(self, user_email: EmailStr) -> User | None:
        """Fetch a user by email."""
        return await User.find_one({"email": user_email})