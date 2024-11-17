from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_db_url:str
    secret_key:str
    algorithm:str
    access_token_expire_minutes:int
    refresh_token_expire_days:int

    class Config:
        env_file="env"

settings=Settings()
