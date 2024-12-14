from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from fastapi import FastAPI
from src.documents.blacklist_token import BlackListToken
from src.documents.study_room import StudyRoom
from src.documents.user_document import UserDocument
from src.documents.friend_request import FriendRequest
from src.documents.invitation import Invitation
from src.config.settings import settings


async def db_lifespan(app: FastAPI):
    app.mongodb_client = AsyncIOMotorClient(settings.mongo_db_url)
    app.database = app.mongodb_client["collaborNote_db"]

    await init_beanie(
        database=app.database,
        document_models=[
            UserDocument,
            BlackListToken,
            FriendRequest,
            StudyRoom,
            Invitation,
        ],
    )

    ping_response = await app.database.command("ping")
    if int(ping_response["ok"]) != 1:
        raise ConnectionError(
            "Unable to connect to the MongoDB cluster. Please check your database connection settings."
        )

    yield

    app.mongodb_client.close()
