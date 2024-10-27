from fastapi import FastAPI
from app.config.database import db_lifespan
from app.routers import user


app = FastAPI(lifespan=db_lifespan)


app.include_router(user.router)