from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from src.config.database import db_lifespan
from src.config.settings import settings
from src.routers import (
    auth,
    user_router,
    friend_requests,
    study_room,
    invitation,
    websocket,
)

from src.utils import http_exception_handler, validation_exception_handler


app = FastAPI(lifespan=db_lifespan)

origins = [
    settings.allowed_origins,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(user_router.router)
api_router.include_router(friend_requests.router)
api_router.include_router(study_room.router)
api_router.include_router(invitation.router)
api_router.include_router(websocket.router)

app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to CollaborNote API!",
        "env_mode": settings.app_environment,
        "allowed_origins": settings.allowed_origins,
    }
