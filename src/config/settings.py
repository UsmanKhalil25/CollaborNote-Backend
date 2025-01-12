from pydantic_settings import BaseSettings
from src.constants import APP_ENVIORNMENT_DEV, APP_ENVIORNMENT_PROD


class Settings(BaseSettings):
    mongo_db_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_days: int
    app_frontend_url: str
    app_localhost_url: str
    app_environment: str

    @property
    def allowed_origins(self):
        if self.app_environment == APP_ENVIORNMENT_DEV:
            return [self.app_localhost_url]
        elif self.app_environment == APP_ENVIORNMENT_PROD:
            return [self.app_frontend_url]
        return []

    class Config:
        env_file = ".env"


settings = Settings()
