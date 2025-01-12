from pydantic import BaseModel


class TokenData(BaseModel):
    token: str
    user_id: str
