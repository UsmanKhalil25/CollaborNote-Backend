from beanie import PydanticObjectId
from enum import Enum

from .base_document import BaseDocument


class FriendRequestStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class FriendRequest(BaseDocument):
    sender_id: PydanticObjectId
    receiver_id: PydanticObjectId
    status: FriendRequestStatus = FriendRequestStatus.PENDING

    class Settings:
        collection = "friend_requests"
