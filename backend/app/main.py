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
# from supabase import create_client, Client
from app.utils.schema_generator import generate_schema
from app.models.user import User
from app.models.chat import ChatCollection, Conversation, Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer()  
token_verifier = TokenVerifier()
   
# supabase: Client = create_client(
#     settings.SUPABASE.URL,
#     settings.SUPABASE.KEY
# )

app = FastAPI(
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

PUBLIC_PATHS = [
    "/",
    "/api/users/signup",
    "/openapi.json",
    "/api/users/login",
    "/api/users/all",
    "/docs",
    "/redoc",
    # "/test-supabase",
]

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
    
    # Skip auth for public paths
    if request.url.path in PUBLIC_PATHS or any(request.url.path.startswith(prefix) for prefix in PUBLIC_PREFIXES):
        logger.debug(f"Skipping auth for public path: {request.url.path}")
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
