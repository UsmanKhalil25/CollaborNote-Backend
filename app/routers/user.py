from fastapi import APIRouter,status,Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.controllers.user_controller import UserController
from app.schemas import UserCreate, UserLogin
from app.secutiry import oauth2_scheme

router = APIRouter(
    prefix="/api/users",
    tags=['Users']
)

def get_user_controller():
    return UserController()

@router.post("/register",status_code=status.HTTP_201_CREATED)
async def register(user:UserCreate,user_controller:UserController=Depends(get_user_controller)):
    await user_controller.register_user(user)
    return {"message":"User registered successfully"}


@router.post("/login")
async def login(user_credentials:UserLogin,user_controller:UserController=Depends(get_user_controller)):
    access_token=await user_controller.login_user(user_credentials)
    return {"access_token":access_token,"token_type":"bearer"}


@router.post("/logout")
async def logout(token:str=Depends(oauth2_scheme),user_controller:UserController=Depends(get_user_controller)):
    await user_controller.make_token_blacklist(token)
    return {"message": "Logout successful"}