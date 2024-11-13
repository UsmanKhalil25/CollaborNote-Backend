from datetime import datetime
from typing import List
from app.models.friend_request import FriendRequest, FriendRequestStatus
from app.services.user_service import UserService
from app.utils import validate_object_id, convert_to_pydantic_object_id
from fastapi import HTTPException, status

class FriendRequestService:
    @staticmethod
    async def get_received_requests(user_id: str, user_service: UserService) -> List[FriendRequest]:
        validate_object_id(user_id)
        user_object_id = convert_to_pydantic_object_id(user_id)

        # calling this only to be sure user is present (no need to store the user)
        await user_service.get_user_by_id(user_object_id)

        received_requests = await FriendRequest.find(FriendRequest.receiver_id == user_object_id).to_list()
        
        return received_requests

    @staticmethod
    async def send_friend_request(from_user_id: str, to_user_id: str, user_service: UserService):
        validate_object_id(from_user_id)
        validate_object_id(to_user_id)

        from_user_object_id = convert_to_pydantic_object_id(from_user_id)
        to_user_object_id = convert_to_pydantic_object_id(to_user_id)

        from_user = await user_service.get_user_by_id(from_user_object_id)
        to_user = await user_service.get_user_by_id(to_user_object_id)

        if user_service.check_if_already_friends(to_user, from_user_object_id) or user_service.check_if_already_friends(from_user, to_user_object_id) :
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already friends with this user"
            )

        existing_request = await FriendRequest.find_one(
            FriendRequest.sender_id == from_user_object_id,
            FriendRequest.receiver_id == to_user_object_id,
            FriendRequest.status == FriendRequestStatus.PENDING 
        )
        if existing_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A friend request already exists between these users"
            )

        existing_request = await FriendRequest.find_one(
            FriendRequest.receiver_id == from_user_object_id,
            FriendRequest.sender_id == to_user_object_id,
            FriendRequest.status == FriendRequestStatus.PENDING 
        )
        if existing_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A friend request already exists between these users"
            )

        friend_request = FriendRequest(
            sender_id=from_user_object_id,
            receiver_id=to_user_object_id,
            status=FriendRequestStatus.PENDING
        )
        await friend_request.insert()

        from_user.friend_requests_sent.append(to_user_object_id)
        to_user.friend_requests_received.append(from_user_object_id)
        await from_user.save()
        await to_user.save()

        return friend_request

    @staticmethod
    async def update_request_status(request_id: str, new_state: str, user_service: UserService):
        validate_object_id(request_id)

        normalized_state = new_state.upper()
        valid_state = FriendRequestStatus.__members__.get(normalized_state)
        if not valid_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state"
            )

        request_object_id = convert_to_pydantic_object_id(request_id)
        friend_request = await FriendRequest.get(request_object_id)
        if not friend_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friend request not found"
            )

        if friend_request.status == valid_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The request is already in the desired state"
            )

        if friend_request.status in {FriendRequestStatus.ACCEPTED, FriendRequestStatus.REJECTED} and normalized_state == "PENDING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot revert to pending from accepted or rejected"
            )

        if friend_request.status == FriendRequestStatus.REJECTED and normalized_state == "ACCEPTED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot accept a rejected friend request"
            )

        if friend_request.status == FriendRequestStatus.ACCEPTED and normalized_state == "REJECTED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reject an accepted friend request"
            )

        friend_request.status = valid_state
        friend_request.responded_at = datetime.now()

        if valid_state == FriendRequestStatus.ACCEPTED:
            # TODO: Add notification logic
            await user_service.add_friend(str(friend_request.sender_id), str(friend_request.receiver_id))

        await friend_request.save()

        return friend_request

