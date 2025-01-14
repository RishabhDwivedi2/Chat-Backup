# app/services/chat_admin_service.py

from sqlalchemy.orm import Session
from app.models.chat_admin import ChatAdmin
from app.schemas.chat_admin import ChatAdminCreate
from app.utils.security import get_password_hash, verify_password
from datetime import datetime
from app.services.google_workspace_service import GoogleWorkspaceService
import logging

logger = logging.getLogger(__name__)
workspace_service = GoogleWorkspaceService()

async def create_admin(db: Session, admin: ChatAdminCreate):
    """Create a new admin and their corresponding Google Workspace account"""
    try:
        # First create the admin in our database
        hashed_password = get_password_hash(admin.admin_password)
        db_admin = ChatAdmin(
            admin_first_name=admin.admin_first_name,
            admin_last_name=admin.admin_last_name,
            admin_email=admin.admin_email,
            admin_password=hashed_password,
            company_name=admin.company_name,
            company_type=admin.company_type
        )
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)

        # Create Google Workspace account
        workspace_result = await workspace_service.create_workspace_user(
            first_name=admin.admin_first_name,
            last_name=admin.admin_last_name,
            company_name=admin.company_name
        )

        if workspace_result:
            # Update admin record with assistant email details
            db_admin.assistant_email = workspace_result['email']
            db_admin.assistant_email_created_at = datetime.utcnow()
            db_admin.is_assistant_email_generated = True
            db.commit()
            db.refresh(db_admin)
            logger.info(f"Successfully created admin and workspace account for {admin.admin_email}")
        else:
            logger.error(f"Failed to create workspace account for {admin.admin_email}")
            # Note: Admin account is still created even if workspace creation fails
            # You might want to implement cleanup or retry logic here

        return db_admin

    except Exception as e:
        logger.error(f"Error in create_admin: {str(e)}")
        db.rollback()
        raise

def get_admin_by_email(db: Session, email: str):
    return db.query(ChatAdmin).filter(ChatAdmin.admin_email == email).first()

def authenticate_admin(db: Session, email: str, password: str):
    admin = get_admin_by_email(db, email)
    if not admin:
        return False
    if not verify_password(password, admin.admin_password):
        return False
    return admin