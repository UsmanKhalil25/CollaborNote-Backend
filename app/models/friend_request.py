from beanie import PydanticObjectId, Document
from datetime import datetime
from typing import Optional
from enum import Enum

class FriendRequestStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class FriendRequest(Document):
    sender_id: PydanticObjectId  
    receiver_id: PydanticObjectId  
    status: FriendRequestStatus = FriendRequestStatus.PENDING  
    created_at: datetime = datetime.now()  
    responded_at: Optional[datetime] = None

    class Settings:
        collection = "friend_requests"  
