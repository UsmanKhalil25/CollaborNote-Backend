from typing import Optional
from app.config.setting import settings
from jose import jwt, JWTError
from app.schemas import TokenData
from datetime import datetime, timedelta

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

    def create_access_token(self, data: dict) -> str:
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        return self._create_token(data, expires_delta)

    def create_refresh_token(self, data: dict) -> str:
        expires_delta = timedelta(days=self.refresh_token_expire_days)
        return self._create_token(data, expires_delta)


    def verify_token(self, token: str) -> Optional[str]:
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
                return None  # Return None if user_id is not found
            return user_id  # Return the user_id if the token is valid
        except JWTError as e:
            print(f"JWT error: {e}")
            return None