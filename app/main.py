from fastapi import FastAPI, APIRouter
from app.routers import user
from app.config.database import db_lifespan
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(lifespan=db_lifespan)

origins = [
    "http://localhost:5173/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

api_router.include_router(user.router)

app.include_router(api_router)
