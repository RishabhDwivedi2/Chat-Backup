# app/middleware/auth_middleware.py

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.utils.jwt import decode_jwt
import logging
from app.services.user_service import get_user_by_email
from app.database import SessionLocal
    
logger = logging.getLogger(__name__)

PUBLIC_PATHS = ["/api/users/signup", "/api/users/login", "/docs", "/openapi.json", "/", "/api/users/all"]

async def auth_middleware(request: Request, call_next):
    if request.url.path in PUBLIC_PATHS or request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
        return await call_next(request)

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning(f"Missing Authorization header for {request.url.path}")
            return JSONResponse(status_code=401, content={"detail": "Missing Authorization header"})
        
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            logger.warning(f"Invalid authentication scheme for {request.url.path}")
            return JSONResponse(status_code=401, content={"detail": "Invalid authentication scheme"})
        
        payload = decode_jwt(token)
        if not payload:
            logger.warning(f"Invalid token for {request.url.path}")
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        
        db = SessionLocal()
        try:
            user = get_user_by_email(db, payload["sub"])
            if not user:
                logger.warning(f"User not found for email: {payload['sub']}")
                return JSONResponse(status_code=401, content={"detail": "User not found"})
            
            # Set both the full user object and the user_id in request state
            request.state.user = {
                "id": user.id,
                "email": payload["sub"],
                "name": user.name,
                "role_category": user.role_category
            }
        finally:
            db.close()

        return await call_next(request)
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return JSONResponse(
            status_code=401,
            content={"detail": "Authentication failed"}
        )