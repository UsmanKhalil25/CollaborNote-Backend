from fastapi import HTTPException, status, Response
from src.documents.blacklist_token import BlackListToken
from src.documents.user_document import UserDocument
from src.schemas.user import UserCreate, UserLogin
from src.utils import hash_password, verify_password
from src.services.user_service import UserService
from src.auth.token_manager import TokenManager


class AuthService:
    @staticmethod
    def _set_refresh_token(response: Response, token: str):
        response.set_cookie(
            key="refresh_token",
            value=token,
            httponly=True,
            secure=True,
            samesite="strict",
        )

    @staticmethod
    async def register(user: UserCreate, user_service: UserService) -> None:
        """Register a new user, ensuring the email is unique."""
        existing_user = await user_service.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = hash_password(password=user.password)

        new_user = UserDocument(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            password=hashed_password,
        )
        await new_user.insert()

    async def login(
        self,
        response: Response,
        user_login: UserLogin,
        user_service: UserService,
        token_manager: TokenManager,
    ) -> dict:
        """Authenticate user and return access token while setting refresh token as HttpOnly cookie."""
        existing_user = await user_service.get_user_by_email(user_login.email)
        if not existing_user or not verify_password(
            plain_password=user_login.password, hashed_password=existing_user.password
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
            )

        access_token = token_manager.create_access_token(
            {"user_id": str(existing_user.id)}
        )
        refresh_token = token_manager.create_refresh_token(
            {"user_id": str(existing_user.id)}
        )

        self._set_refresh_token(response, refresh_token)

        return access_token

    @staticmethod
    async def blacklist_token(token: str) -> None:
        """Blacklist the token for logout."""

        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token missing or malformed",
            )
        token = BlackListToken(token=token)
        await token.insert()

    async def refresh_token(
        self, response: Response, token_manager: TokenManager
    ) -> str:
        """Validate the refresh token, generate a new access token, and rotate the refresh token."""
        refresh_token = response.request.cookies.get("refresh_token")

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is missing",
            )

        user_id = token_manager.verify_refresh_token(refresh_token)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        new_access_token = token_manager.create_access_token(data={"user_id": user_id})
        new_refresh_token = token_manager.create_refresh_token(
            data={"user_id": user_id}
        )

        self._set_refresh_token(response, new_refresh_token)

        return new_access_token
