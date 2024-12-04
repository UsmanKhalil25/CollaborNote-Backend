from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from fastapi import FastAPI
from app.models.blacklist_token import BlackListToken
from app.models.study_room import StudyRoom
from app.models.user import User
from app.models.friend_request import FriendRequest
from app.models.invitation import Invitation
from app.config.setting import settings

async def db_lifespan(app: FastAPI):
    app.mongodb_client = AsyncIOMotorClient(settings.mongo_db_url)
    app.database = app.mongodb_client["collaborNote_db"] 

    await init_beanie(database=app.database, document_models=[User, BlackListToken, FriendRequest, StudyRoom, Invitation])

    ping_response = await app.database.command("ping")
    if int(ping_response["ok"]) != 1:
        raise ConnectionError("Unable to connect to the MongoDB cluster. Please check your database connection settings.")

    yield

    app.mongodb_client.close()
