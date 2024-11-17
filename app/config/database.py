# from fastapi import FastAPI
# from beanie import init_beanie
# import gridfs
# from motor.motor_asyncio import AsyncIOMotorClient
# from app.models.blacklist_token import BlackListToken
# from app.models.study_room import StudyRoom
# from app.models.user import User
# from app.models.friend_request import FriendRequest
# from app.config.setting import settings


# async def db_lifespan(app: FastAPI):
#     # Startup
#     app.mongodb_client = AsyncIOMotorClient(settings.mongo_db_url)
#     app.database = app.mongodb_client["collaborNote_db"]
#     app.state.fs = gridfs.AsyncGridFSBucket(app.database)

#     await init_beanie(database=app.database, document_models=[User, BlackListToken, FriendRequest,StudyRoom]) 

#     ping_response = await app.database.command("ping")

#     if int(ping_response["ok"]) != 1:
#         raise Exception("Problem connecting to database cluster.")

#     yield

#     # Shutdown
#     app.mongodb_client.close()



from motor.motor_asyncio import AsyncIOMotorClient
import gridfs
from beanie import init_beanie
from fastapi import FastAPI
from app.models.blacklist_token import BlackListToken
from app.models.study_room import StudyRoom
from app.models.user import User
from app.models.friend_request import FriendRequest
from app.config.setting import settings

async def db_lifespan(app: FastAPI):
    # Startup
    app.mongodb_client = AsyncIOMotorClient(settings.mongo_db_url)
    app.database = app.mongodb_client["collaborNote_db"] 

    await init_beanie(database=app.database, document_models=[User, BlackListToken, FriendRequest, StudyRoom])

    # Check if MongoDB is available
    ping_response = await app.database.command("ping")
    if int(ping_response["ok"]) != 1:
        raise Exception("Problem connecting to database cluster.")

    yield

    # Shutdown
    app.mongodb_client.close()


    # # Ensure `app.database` is an instance of AsyncIOMotorDatabase
    # if not isinstance(app.database, AsyncIOMotorClient):
    #     raise TypeError("app.database must be an instance of AsyncIOMotorDatabase")

    # # Create the GridFS bucket from the database
    # app.state.fs = gridfs.AsyncGridFSBucket(app.database)