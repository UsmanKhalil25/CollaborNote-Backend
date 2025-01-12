from typing import Optional
from src.documents.blacklist_token_document import BlackListToken


class BlacklistTokenRepository:
    """Repository for managing blacklisted tokens."""

    @staticmethod
    async def is_token_blacklisted(token: str) -> bool:
        """Check if a token exists in the blacklist."""
        return await BlackListToken.find_one(BlackListToken.token == token) is not None

    @staticmethod
    async def save_token(token: str) -> None:
        """Save a token to the blacklist."""
        await BlackListToken(token=token).insert()
