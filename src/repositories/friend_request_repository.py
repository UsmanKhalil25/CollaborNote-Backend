from typing import List
from src.documents.friend_request import FriendRequest


class FriendRequestRepository:

    @staticmethod
    async def search_by_query(query: dict) -> List[FriendRequest]:
        friend_requests = await FriendRequest.find_many(query).to_list()
        return friend_requests
