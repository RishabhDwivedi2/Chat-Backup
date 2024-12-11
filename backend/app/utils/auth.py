# app/utils/auth.py

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
from app.utils.jwt import decode_jwt

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_user(
    request: Request,
    auth_credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[dict]:
    """Get current authenticated user from JWT token"""
    try:
        token = auth_credentials.credentials.strip()
        logger.debug(f"Processing token (first 20 chars): {token[:20]}")
        
        payload = decode_jwt(token)
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
        
        request.state.user = payload
        return payload
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )