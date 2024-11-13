from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from passlib.context import CryptContext
from bson import ObjectId
from beanie import PydanticObjectId
from typing import Any, Dict
from app.constants import RESPONSE_STATUS_ERROR



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
            "status": RESPONSE_STATUS_ERROR,
            "message": exc.detail,
            "data": None,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "status": RESPONSE_STATUS_ERROR,
            "message": "Validation error",
            "data": exc.errors(),
        },
    )


def validate_object_id(id: str):
    """Validates the given ID format."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )

def convert_to_pydantic_object_id(id: str) -> PydanticObjectId:
    """Converts a string ID to a PydanticObjectId."""
    return PydanticObjectId(id)
