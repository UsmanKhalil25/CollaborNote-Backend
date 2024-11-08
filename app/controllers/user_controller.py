from app.schemas import UserCreate, UserLogin
from app.services.user_service import UserService


class UserController:
    def __init__(self, user_service: UserService = None):
        self.user_service = user_service or UserService()

    async def register_user(self, user: UserCreate) -> None:
        await self.user_service.register_user(user=user)

    async def login_user(self, user_login: UserLogin) -> str:
        return await self.user_service.login_user(user_login)

    async def make_token_blacklist(self, token: str) -> None:
        await self.user_service.make_token_blacklist(token=token)
