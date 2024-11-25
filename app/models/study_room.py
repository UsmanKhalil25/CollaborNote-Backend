from datetime import datetime
from typing import List, Optional
from beanie import Document

from app.schemas.participant import Participant

class StudyRoom(Document):
    name: str
    description: str
    participants: List[Participant] = []  
    content: str = ""
    is_active: bool = True
    created_at: datetime = datetime.now()
    ended_at: Optional[datetime] = None

    class Settings:
        collection = "study_rooms"
