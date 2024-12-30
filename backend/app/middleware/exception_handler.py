from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.app.config.constants import settings
from typing import Dict, Any

def add_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        status_code = 500
        content: Dict[str, Any] = {"message": "Internal Server Error"}

        if settings.ENV.DEBUG:
            content.update({
                "detail": str(exc),
                "type": type(exc).__name__,
            })

        return JSONResponse(status_code=status_code, content=content)
