from datetime import datetime, timezone
from beanie import Document, PydanticObjectId
from pydantic import Field


class BaseDocument(Document):
    _id: PydanticObjectId
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        abstract = True
