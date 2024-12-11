# app/routers/user_router.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.schemas.user import UserCreate, UserInDB, Token, UserLoginResponse
from app.database import get_db
from app.services import user_service
from app.utils.jwt import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
import logging
from app.schemas.user import ThemeUpdate
from fastapi import Body
from app.utils.auth import get_current_user
from datetime import timedelta
from app.config import settings


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/signup", response_model=Token, operation_id="user_signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    logger = logging.getLogger(__name__)
    logger.info(f"Received signup data: {user}")
    try:
        if user.password != user.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        db_user = user_service.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        new_user = user_service.create_user(db=db, user=user)
        access_token = create_access_token(data={"sub": new_user.email})
        logger.info(f"User successfully created with email: {new_user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        logger.error(f"HTTP exception during signup: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
@router.post("/login", response_model=UserLoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for email: {form_data.username}")
    try:
        user = user_service.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"Invalid credentials for email: {form_data.username}")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        # Create access token with simple payload
        token_data = {
            "sub": user.email,
            "type": "access"
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.JWT.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Log token details for debugging
        logger.debug(f"Generated token for user: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserInDB.from_orm(user)
        }
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    

# New endpoint to verify token and return user details
@router.get("/verify-token", response_model=UserInDB, operation_id="verify_token")
async def verify_token(request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    db_user = user_service.get_user_by_email(db, email=user["sub"])
    if db_user is None:
        logger.warning(f"User not found for email: {user['sub']}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Token verified for user: {user['sub']}")
    return UserInDB.from_orm(db_user)    

@router.get("/all", response_model=List[UserInDB], operation_id="get_all_users")
async def get_all_users(db: Session = Depends(get_db)):
    logger.info("Retrieving all users")
    try:
        users = user_service.get_all_users(db)
        logger.info(f"Retrieved {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Unexpected error while retrieving users: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving users")

@router.get("/me", response_model=UserInDB, operation_id="get_current_user")
async def read_users_me(request: Request, db: Session = Depends(get_db)):
    logger.info("Accessing user profile")
    user = request.state.user
    db_user = user_service.get_user_by_email(db, email=user["sub"])
    if db_user is None:
        logger.warning(f"User not found for email: {user['sub']}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User profile accessed for email: {user['sub']}")
    return db_user

@router.put("/me/theme", response_model=UserInDB, operation_id="update_user_theme")
async def update_user_theme(
    request: Request,  
    db: Session = Depends(get_db),
    theme_update: ThemeUpdate = Body(...),
):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db_user = user_service.get_user_by_email(db, email=user["sub"])  # 'sub' is the user email from the JWT
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.color = theme_update.color
    db_user.mode = theme_update.mode
    db.commit()
    db.refresh(db_user)
    return UserInDB.from_orm(db_user)
