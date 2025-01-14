# app/routers/chat_admin_router.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.schemas.chat_admin import ChatAdminCreate, ChatAdminInDB, Token, ChatAdminLoginResponse
from app.database import get_db
from app.services import chat_admin_service
from app.utils.jwt import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
import logging
from datetime import timedelta
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/signup", response_model=Token, operation_id="chat_admin_signup")
async def signup(admin: ChatAdminCreate, db: Session = Depends(get_db)):
    logger.info(f"Received signup data for admin: {admin.admin_email}")
    try:
        # Validate passwords match
        if admin.admin_password != admin.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        # Check if email already exists
        db_admin = chat_admin_service.get_admin_by_email(db, email=admin.admin_email)
        if db_admin:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create admin and workspace account
        new_admin = await chat_admin_service.create_admin(db=db, admin=admin)
        
        # Generate access token
        access_token = create_access_token(
            data={"sub": new_admin.admin_email},
            expires_delta=timedelta(minutes=settings.JWT.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Check if workspace account was created
        if not new_admin.is_assistant_email_generated:
            logger.warning(f"Workspace account creation failed for {admin.admin_email}")
            # You might want to add this info to the response
        
        logger.info(f"Admin successfully created with email: {new_admin.admin_email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException as e:
        logger.error(f"HTTP exception during signup: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post("/login", response_model=ChatAdminLoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for admin email: {form_data.username}")
    try:
        admin = chat_admin_service.authenticate_admin(db, form_data.username, form_data.password)
        if not admin:
            logger.warning(f"Invalid credentials for admin email: {form_data.username}")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        token_data = {
            "sub": admin.admin_email,
            "type": "access"
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.JWT.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "admin": ChatAdminInDB.from_orm(admin)
        }
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")