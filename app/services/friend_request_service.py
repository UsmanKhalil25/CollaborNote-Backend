from fastapi import HTTPException, status
from datetime import datetime
from typing import List
from app.models.friend_request import FriendRequest, FriendRequestStatus
from app.models.user import User
from app.services.user_service import UserService
from app.utils import validate_object_id, convert_to_pydantic_object_id

class FriendRequestService:

    @staticmethod
    async def get_received_requests(user_id: str, user_service: UserService) -> List[dict]:
        validate_object_id(user_id)
        user_object_id = convert_to_pydantic_object_id(user_id)

        await user_service.get_user_by_id(user_object_id)

        received_requests = await FriendRequest.find(FriendRequest.receiver_id == user_object_id).to_list()

        requests_with_senders = []
        for friend_request in received_requests:
            sender_user = await User.get(friend_request.sender_id)
            if sender_user:
                request_data = {
                    "friend_request": friend_request,
                    "sender": {
                        "_id": str(sender_user.id),
                        "first_name": sender_user.first_name,
                        "last_name": sender_user.last_name,
                        "email": sender_user.email
                    }
                }
                requests_with_senders.append(request_data)

        return requests_with_senders


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

        from_user.friend_requests_sent.append(friend_request.id)
        to_user.friend_requests_received.append(friend_request.id)
        await from_user.save()
        await to_user.save()

        return friend_request

    @staticmethod
    async def update_request_status(user_id: str, request_id: str, new_state: str, user_service: UserService):
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

        user_object_id = convert_to_pydantic_object_id(user_id)

        user = await user_service.get_user_by_id(user_object_id)
        print(user.friend_requests_received)
        if convert_to_pydantic_object_id(request_id) not in user.friend_requests_received:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this friend request"
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
            # doing this to remove any other mutual request between the users
            existing_request = await FriendRequest.find_one(
                FriendRequest.receiver_id == friend_request.sender_id,
                FriendRequest.sender_id == friend_request.receiver_id,
                FriendRequest.status == FriendRequestStatus.PENDING
            )

            if existing_request:
                await existing_request.delete()

            await user_service.add_friend(str(friend_request.sender_id), str(friend_request.receiver_id))

        await friend_request.save()

        return friend_request

