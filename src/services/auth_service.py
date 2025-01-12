from fastapi import HTTPException, status, Response

from src.repositories.user_repository import UserRepository
from src.repositories.blacklist_token_repository import BlacklistTokenRepository
from src.schemas.user import UserRegister, UserLogin
from src.utils import hash_password, verify_password
from src.services.token_service import TokenService
from src.constants import REFRESH_TOKEN_COOKIE


class AuthService:
    """Service for handling authentication-related operations."""

    def __init__(self):
        self.user_repository = UserRepository()
        self.blacklist_token_repository = BlacklistTokenRepository()
        self.token_service = TokenService()

    @staticmethod
    def _set_refresh_token(response: Response, token: str):
        """Set the refresh token as an HttpOnly cookie in the response."""

        response.set_cookie(
            key=REFRESH_TOKEN_COOKIE,
            value=token,
            httponly=True,
            secure=True,
            samesite="strict",
        )

    async def register(self, user_data: UserRegister) -> None:
        """Register a new user."""

        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = hash_password(password=user_data.password)
        user_dict = user_data.model_dump()
        user_dict["password"] = hashed_password

        await self.user_repository.create(user_data=user_dict)

    async def login(
        self,
        user_data: UserLogin,
        response: Response,
    ) -> str:
        """Authenticate user and return an access token."""

        existing_user = await self.user_repository.get_by_email(user_data.email)
        if not existing_user or not verify_password(
            plain_password=user_data.password, hashed_password=existing_user.password
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
            )

        access_token = self.token_service.create_access_token(
            {"user_id": str(existing_user.id)}
        )
        refresh_token = self.token_service.create_refresh_token(
            {"user_id": str(existing_user.id)}
        )

        self._set_refresh_token(response, refresh_token)
        return access_token

    async def refresh_token(self, response: Response) -> str:
        """Generate a new access token and rotate the refresh token."""

        refresh_token = response.request.cookies.get(REFRESH_TOKEN_COOKIE)

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is missing",
            )

        user_id = self.token_service.verify_token(refresh_token)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        new_access_token = self.token_service.create_access_token(
            data={"user_id": user_id}
        )
        new_refresh_token = self.token_service.create_refresh_token(
            data={"user_id": user_id}
        )

        self._set_refresh_token(response, new_refresh_token)

        return new_access_token

    async def blacklist_token(self, token: str) -> None:
        """Blacklist the token for logout."""

        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token missing or malformed",
            )

        await self.blacklist_token_repository.save_token(token=token)
