from datetime import datetime
from typing import Optional
from beanie import Document,PydanticObjectId
from app.schemas.invitation import InvitationStatus

class Invitation(Document):
    study_room_id:  PydanticObjectId
    invited_user_id: PydanticObjectId  
    inviter_user_id: PydanticObjectId  
    status: str = InvitationStatus.PENDING
    created_at: datetime = datetime.now()
    responded_at: Optional[datetime] = None

    class Settings:
        collection = "invitations"
