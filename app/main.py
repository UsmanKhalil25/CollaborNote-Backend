from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import db_lifespan
from app.routers import auth, users, friend_requests
from app.utils import http_exception_handler, validation_exception_handler

app = FastAPI(lifespan=db_lifespan)

origins = [
    "http://localhost:5173",
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
api_router.include_router(users.router)
api_router.include_router(friend_requests.router)

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to CollaborNote API!"}
