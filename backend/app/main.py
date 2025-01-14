# app/main.py

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.routers import user_router, entries
from app.middleware.cors import add_cors_middleware
from app.config import settings
from app.database import SessionLocal
from app.utils.jwt import decode_jwt
import logging
import time
from app.routers import chat_router  
from typing import Optional
from app.routers.gateway_router import router as gateway_router
from app.cache.token_cache import TokenVerifier
from app.middleware.session_middleware import SessionMiddleware 
from firebase_admin import storage
from contextlib import asynccontextmanager
from app.utils.schema_generator import generate_schema
from app.models.user import User
from app.models.chat import ChatCollection, Conversation, Message
from app.routers.gmail_router import router as gmail_router
from app.services.redis.redis_service import RedisService
from app.routers.chat_admin_router import router as chat_admin_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer()  
token_verifier = TokenVerifier()
redis_service = RedisService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting up application...")
    
    # Check Redis status on startup
    if redis_service._init_redis():
        logger.info("✅ Redis connection established successfully")
    else:
        logger.warning("⚠️ Redis connection failed - running without Redis")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    try:
        redis_service.close()
        logger.info("Successfully cleaned up Redis connection")
    except Exception as e:
        logger.error(f"Error during shutdown cleanup: {str(e)}")
   
app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT.NAME,
    debug=settings.ENV.DEBUG,
    openapi_tags=[{
        "name": "chat",
        "description": "Chat operations"
    }],
    openapi_schema={
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "security": [{"BearerAuth": []}]
    }
)

add_cors_middleware(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS.ORIGINS,
    allow_credentials=settings.CORS.ALLOW_CREDENTIALS,
    allow_methods=settings.CORS.ALLOW_METHODS,
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

app.add_middleware(SessionMiddleware)

BASE_PUBLIC_PATHS = [
    "/",
    "/api/users/signup",
    "/openapi.json",
    "/api/users/login",
    "/api/users/all",
    "/docs",
    "/redoc",
    "/auth/google",
    "/setup-gmail-watch",
    "/watch-gmail",
    "/gmail-webhook",
    "/auth/status",
    "/auth/google/callback",
    "/clear-tokens",
    "/clear-gmail-watch",
    "/reset-gmail-auth"
]

# Chat router paths that should be public in testing mode
CHAT_PATHS = [
    "/api/chat",
    "/api/chat/",
    "/api/chat/collections",
    "/api/chat/conversations/"
]

# Set PUBLIC_PATHS based on testing mode
PUBLIC_PATHS = BASE_PUBLIC_PATHS + (CHAT_PATHS if settings.APP['TESTING_MODE'] else [])

PUBLIC_PREFIXES = ["/docs"]

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time:.2f}s")
    return response

@app.middleware("http")
async def handle_headers(request: Request, call_next):
    try:
        for key, value in request.headers.items():
            if any(ord(c) > 255 for c in value):
                value = value.encode('utf-8').decode('iso-8859-1')
                request.headers.__dict__["_list"].append((key.lower(), value))
        
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Header processing error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid header encoding"}
        )

async def get_current_user(
    request: Request,
    auth_credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> Optional[dict]:
    """Dependency to get current authenticated user with caching"""
    try:
        token = auth_credentials.credentials
        
        # Use token verifier with caching
        payload = await token_verifier.verify_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
            
        logger.debug(f"Successfully verified token for user: {payload.get('sub')}")
        return payload
        
    except Exception as e:
        logger.error(f"Authentication error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Authentication middleware with token caching"""
    
    if settings.APP['TESTING_MODE']:
        # For testing mode, check if path starts with any of our patterns
        path = request.url.path
        is_chat_path = any(path.startswith(pattern) for pattern in CHAT_PATHS)
        is_base_public = path in BASE_PUBLIC_PATHS
        
        if is_chat_path or is_base_public:
            request.state.user = {"sub": settings.APP['TEST_USER_EMAIL']}
            return await call_next(request)

    # Check if the path EXACTLY matches any of the public paths
    if path in BASE_PUBLIC_PATHS:
        return await call_next(request)
    
    # Or if it matches the callback pattern with query parameters
    if path.startswith("/auth/google/callback"):
        return await call_next(request)

    try:
        logger.debug(f"Processing authentication for path: {request.url.path}")
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            logger.warning("No Authorization header found")
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing Authorization header"}
            )

        if not auth_header.strip().startswith("Bearer "):
            logger.warning("Invalid auth header format - missing Bearer prefix")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authentication scheme"}
            )
        
        token = auth_header.replace("Bearer", "", 1).strip()
        if not token:
            logger.warning("Empty token received")
            return JSONResponse(
                status_code=401,
                content={"detail": "Empty token"}
            )

        # Use token verifier with caching
        payload = await token_verifier.verify_token(token)
        if not payload:
            logger.warning("Token validation failed")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )

        # Store user info in request state
        request.state.user = payload
        logger.debug(f"Successfully authenticated user: {payload.get('sub')}")

        return await call_next(request)

    except Exception as e:
        logger.error(f"Authentication middleware error: {str(e)}")
        return JSONResponse(
            status_code=401,
            content={"detail": "Authentication failed"}
        )

@app.get("/secure-endpoint", dependencies=[Depends(bearer_scheme)])
async def secure_endpoint():
    return {"message": "You are authorized!"}

app.include_router(user_router.router, prefix="/api/users", tags=["users"])
app.include_router(entries.router, prefix="/api/entries", tags=["entries"])
app.include_router(chat_router.router, prefix="/api/chat", tags=["chat"]) 
app.include_router(gateway_router, prefix="/api/gateway", tags=["gateway"])
app.include_router(gmail_router)  
app.include_router(chat_admin_router, prefix="/api/chat-admin", tags=["chat-admin"])

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )
    
@app.get("/")
async def root():
    return {"message": "Welcome to the API"}               

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {settings.PROJECT.NAME} in {settings.ENV.APP_ENV} environment")
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER.HOST,
        port=settings.SERVER.PORT,
        log_level="info",
        reload=settings.ENV.DEBUG,
    )
