from fastapi import HTTPException, status
from pydantic import EmailStr
from app.models.blacklist_token import BlackListToken
from app.models.user import User
from app.schemas import UserCreate, UserLogin
from app.security import create_access_token
from app.utils import hash_password, verify_password

class UserService:

    async def get_user(self, user_email: EmailStr) -> User | None:
        """Fetch a user by email."""
        return await User.find_one({"email": user_email})
    
    async def register_user(self, user: UserCreate) -> None:
        """Register a new user, ensuring the email is unique."""
        existing_user = await self.get_user(user_email=user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        hashed_password = hash_password(password=user.password)

        new_user = User(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            password=hashed_password,
        )
        await new_user.insert()
        
    async def login_user(self, user_login: UserLogin) -> str:
        """Authenticate user and return access token."""
        existing_user = await self.get_user(user_email=user_login.email)
        if not existing_user or not verify_password(
            plain_password=user_login.password,
            hashed_password=existing_user.password
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid credentials"
            )
        
        access_token = create_access_token(data={
            "user_id": str(existing_user.id)
        })
        return access_token

    async def make_token_blacklist(self, token: str) -> None:
        """Blacklist the token for logout."""
        blacklist_token = BlackListToken(token=token)
        await blacklist_token.insert()
