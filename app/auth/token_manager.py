from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.schemas.token import TokenData
from app.config.setting import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class TokenManager:
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days

    def _create_token(self, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def _verify_token(self, token: str) -> Optional[str]:
        """Verify and decode the refresh token, returning the user_id if valid."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )
            user_id = payload.get("user_id")
            if user_id is None:
                return None
            return user_id
        except JWTError as e:
            print(f"JWT error: {e}")
            return None

    def create_access_token(self, data: dict) -> str:
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        return self._create_token(data, expires_delta)

    def create_refresh_token(self, data: dict) -> str:
        expires_delta = timedelta(days=self.refresh_token_expire_days)
        return self._create_token(data, expires_delta)

    def get_current_user(self, token: str = Depends(oauth2_scheme)) -> TokenData:
        """Extract and verify the user ID from the access token."""
        user_id = self._verify_token(token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(id=user_id)
