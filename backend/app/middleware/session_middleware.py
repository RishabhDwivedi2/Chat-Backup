# app/middleware/session_middleware.py

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from app.cache.session_manager import session_manager
import logging

logger = logging.getLogger(__name__)

class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Session middleware implementation"""
        try:
            # Get token from request
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer", "", 1).strip()
                
                # Get user payload from request state (set by auth middleware)
                user_payload = getattr(request.state, "user", None)
                
                if user_payload:
                    # Get or create session
                    session_id, session = await session_manager.get_or_create_session(
                        token=token,
                        user_payload=user_payload
                    )
                    
                    # Store session info in request state
                    request.state.session_id = session_id
                    request.state.session = session
                    
                    # Check if we can bypass verifications
                    request.state.bypass_verification = await session_manager.should_bypass_verification(session_id)
                    
                    # Update request count
                    await session_manager.increment_request_count(session_id)
                    
                    logger.debug(f"Session active for user {user_payload['sub']}, bypass: {request.state.bypass_verification}")
                
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Session middleware error: {str(e)}")
            return await call_next(request)