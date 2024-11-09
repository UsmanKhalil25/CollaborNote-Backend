from fastapi import HTTPException, status
from app.models.blacklist_token import BlackListToken
from app.models.user import User
from app.schemas import UserCreate, UserLogin
from app.security import create_access_token
from app.utils import hash_password, verify_password
from app.services.user_service import UserService

class AuthService:

    async def register(self, user: UserCreate, user_service: UserService) -> None:
        """Register a new user, ensuring the email is unique."""
        existing_user = await user_service.get_user_by_email(user.email)
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
        
    async def login(self, user_login: UserLogin, user_service: UserService) -> str:
        """Authenticate user and return access token."""
        existing_user = await user_service.get_user_by_email(user_login.email)
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

    async def blacklist_token(self, token: str) -> None:
        """Blacklist the token for logout."""
        token = BlackListToken(token=token)
        await token.insert()
