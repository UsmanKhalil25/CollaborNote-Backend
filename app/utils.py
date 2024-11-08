from passlib.context import CryptContext
from fastapi import HTTPException
from typing import Any, Dict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError



pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password:str):
    return pwd_context.hash(password)


def verify_password(plain_password:str, hashed_password:str):
    return pwd_context.verify(plain_password, hashed_password)

def create_response(status: str, message: str, data: Any = None) -> Dict:
    return {
        "status": status,
        "message": message,
        "data": data
    }




async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "data": None,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "message": "Validation error",
            "data": exc.errors(),
        },
    )
