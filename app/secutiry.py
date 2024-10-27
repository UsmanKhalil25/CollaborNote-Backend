from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException,status,Depends
from app.config.setting import settings
from jose import jwt,JWTError
from app.models.blackListToken import BlackListToken
from app.models.user import User
from app.schemas import TokenData, UserBase
from datetime import datetime, timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({'exp': expire})
    encode_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encode_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm],options={"verify_exp":True})
        id = payload.get('user_id')
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)
    except JWTError as e:
        print(e)
        raise credentials_exception

    return token_data


async def get_current_user(token: str = Depends(oauth2_scheme)):
    
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    blacklisted_token = await BlackListToken.find_one({"token": token})
    if blacklisted_token:
        raise credentials_exception
    
    token_data = verify_access_token(token, credentials_exception)
    user = await User.get(token_data.id)
    if user is None:
        raise credentials_exception
    current_user=UserBase(
        email=user.email
    )
    return current_user