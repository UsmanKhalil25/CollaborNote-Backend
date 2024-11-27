from datetime import datetime
from typing import Optional
from beanie import Document
from app.schemas.invitation import InvitationStatus

class Invitation(Document):
    study_room_id: str  
    invited_user_id: str  
    inviter_user_id: str  
    status: str = InvitationStatus.PENDING
    created_at: datetime = datetime.now()
    responded_at: Optional[datetime] = None

    class Settings:
        collection = "invitations"
