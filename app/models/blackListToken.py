from typing import Collection
from beanie import Document


class BlackListToken(Document):
    token:str

    class Settings:
        Collection='blacklist-tokens'