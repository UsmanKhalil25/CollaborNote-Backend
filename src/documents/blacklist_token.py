from beanie import Document


class BlackListToken(Document):
    token: str

    class Settings:
        collection = "blacklist_tokens"
