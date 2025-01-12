from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from jose import jwt, JWTError
from datetime import datetime, timedelta

from src.schemas.token import TokenData
from src.repositories.blacklist_token_repository import BlacklistTokenRepository
from src.config.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class TokenService:
    """Service for managing access and refresh tokens, including creation, validation,decoding, and blacklisting."""

    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expiry = settings.jwt_access_token_expire_minutes
        self.refresh_token_expiry = settings.jwt_refresh_token_expire_days

    def _create_token(self, payload: dict, expiry: timedelta) -> str:
        """Create a JWT with the specified payload and expiry time."""

        data_to_encode = payload.copy()
        data_to_encode.update({"exp": datetime.utcnow() + expiry})
        return jwt.encode(data_to_encode, self.secret_key, algorithm=self.algorithm)

    def _decode_token(self, token: str) -> Optional[str]:
        """Decode and verify a JWT, extracting the user ID if valid."""

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True},
            )
            return payload.get("user_id")
        except JWTError as e:
            print(f"Token decoding error: {e}")
            return None

    def _raise_unauthorized_error(
        self, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED
    ) -> HTTPException:
        """Raise an HTTP exception for unauthorized access."""

        return HTTPException(
            status_code=status_code,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    def create_access_token(self, payload: dict) -> str:
        """Create a short-lived access token."""

        expiry = timedelta(minutes=self.access_token_expiry)
        return self._create_token(payload, expiry)

    def create_refresh_token(self, payload: dict) -> str:
        """Create a long-lived refresh token."""

        expiry = timedelta(days=self.refresh_token_expiry)
        return self._create_token(payload, expiry)

    async def validate_access_token(
        self, token: str = Depends(oauth2_scheme)
    ) -> TokenData:
        """Validate an access token, ensuring it's not expired or blacklisted."""

        user_id = self._decode_token(token)
        if not user_id:
            raise self._raise_unauthorized_error("Invalid or expired access token.")

        if await BlacklistTokenRepository.is_token_blacklisted(token=token):
            raise self._raise_unauthorized_error("Access token has been blacklisted.")

        return TokenData(token=token, user_id=user_id)
