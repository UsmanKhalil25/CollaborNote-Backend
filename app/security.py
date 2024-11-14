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
        """Generate a JWT token with expiration."""
        to_encode = data.copy()
        expire = datetime.now() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_access_token(self, data: dict) -> str:
        """Generate an access token with a short expiration time."""
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        return self._create_token(data, expires_delta)

    def create_refresh_token(self, data: dict) -> str:
        """Generate a refresh token with a configurable expiration time."""
        expires_delta = timedelta(days=self.refresh_token_expire_days)
        return self._create_token(data, expires_delta)

    def verify_access_token(self, token: str, credentials_exception):
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )
            user_id = payload.get('user_id')
            if user_id is None:
                raise credentials_exception
            token_data = TokenData(id=user_id)
        except JWTError as e:
            print(e)
            raise credentials_exception

        return token_data

