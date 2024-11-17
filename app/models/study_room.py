from datetime import datetime
from typing import List, Optional
from beanie import Document,PydanticObjectId


class StudyRoom(Document):
    name: str
    description: Optional[str]
    owner_id: PydanticObjectId
    active_participants: List[dict] = []  # List of dictionaries containing participant details
    former_participants: List[PydanticObjectId] = []
    created_at: datetime = datetime.now()
    is_active: bool = True
    markdown_content: str
    last_modified: datetime = datetime.now()

    class Settings:
        collection = "study_rooms"