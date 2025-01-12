from typing import List, Optional
from beanie import PydanticObjectId

from src.documents.friend_request_document import FriendRequest, FriendRequestStatus


class FriendRequestRepository:

    @staticmethod
    async def search_by_query(query: dict) -> List[FriendRequest]:
        """Search for friend requests based on a query."""
        friend_requests = await FriendRequest.find(query).to_list()
        return friend_requests

    @staticmethod
    async def get_by_id(id: PydanticObjectId) -> Optional[FriendRequest]:
        """Retrieve a friend request document by its ID."""
        return await FriendRequest.get(id)

    @staticmethod
    async def update_status(
        friend_request: FriendRequest, new_status: FriendRequestStatus
    ):
        """Update the status of a friend request document."""
        friend_request.status = new_status
        await friend_request.save()
