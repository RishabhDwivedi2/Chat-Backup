# app/utils/jwt.py

from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

def decode_jwt(token: str) -> Optional[dict]:
    """Decode and validate JWT token"""
    try:
        logger.debug("Attempting to decode JWT token")
        secret_key = str(settings.JWT.SECRET_KEY)
        algorithm = settings.JWT.ALGORITHM
        
        # Clean up the token
        token = token.strip()
        if token.lower().startswith('bearer '):
            token = token[7:].strip()
        
        # Additional token format validation
        if not token or '.' not in token:
            logger.error("Invalid token format")
            return None
            
        # Decode the JWT token
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            logger.debug(f"Successfully decoded token for user: {payload.get('sub')}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return None
        except jwt.JWTError as e:
            logger.error(f"JWT decode error: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"Unexpected error decoding JWT: {str(e)}")
        return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token"""
    try:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        secret_key = str(settings.JWT.SECRET_KEY)
        algorithm = settings.JWT.ALGORITHM
        
        logger.debug(f"Creating JWT token with algorithm: {algorithm}")
        
        token = jwt.encode(to_encode, secret_key, algorithm=algorithm)
        
        # Log token length and sample for debugging
        logger.debug(f"Generated token length: {len(token)}")
        logger.debug(f"Token sample (first 20 chars): {token[:20]}")
        
        return token
        
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise