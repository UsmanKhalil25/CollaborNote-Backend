from .base_document import BaseDocument


class BlackListToken(BaseDocument):
    token: str

    class Settings:
        collection = "blacklist_tokens"
