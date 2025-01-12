from datetime import datetime
from pydantic import BaseModel
from .user import UserInfo


class FriendRequestReceived(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    sender_id: str
    receiver_id: str
    status: str
    sender_info: UserInfo
