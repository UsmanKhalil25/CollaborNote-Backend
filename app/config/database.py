from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.blacklist_token import BlackListToken
from app.models.user import User
from app.models.friend_request import FriendRequest
from app.config.setting import settings


async def db_lifespan(app: FastAPI):
    # Startup
    app.mongodb_client = AsyncIOMotorClient(settings.mongo_db_url)
    app.database = app.mongodb_client["collaborNote_db"]

    await init_beanie(database=app.database, document_models=[User, BlackListToken, FriendRequest]) 

    ping_response = await app.database.command("ping")

    if int(ping_response["ok"]) != 1:
        raise Exception("Problem connecting to database cluster.")

    yield

    # Shutdown
    app.mongodb_client.close()