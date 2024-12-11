# [AI]: This file implements CORS (Cross-Origin Resource Sharing) middleware for a FastAPI application.
# It provides functionality to configure CORS settings for the API.
# Key features:
# - Adds CORS middleware to the FastAPI app
# - Uses settings from a configuration file to set CORS parameters
# - Allows customization of origins, credentials, methods, and headers

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app import settings

def add_cors_middleware(app: FastAPI):
    """
    [AI]: This function adds CORS middleware to a FastAPI application.
    It configures the middleware using settings from the application's configuration.

    @param app: The FastAPI application instance to which the middleware will be added
    """
    # [AI]: Add the CORSMiddleware to the FastAPI app with specific configuration
    app.add_middleware(
        CORSMiddleware,
        # [AI]: Set allowed origins from the app settings
        allow_origins=settings.CORS.ORIGINS,
        # [AI]: Configure whether to allow credentials (cookies, authorization headers, etc.)
        allow_credentials=settings.CORS.ALLOW_CREDENTIALS,
        # [AI]: Specify allowed HTTP methods for CORS requests
        allow_methods=settings.CORS.ALLOW_METHODS,
        # [AI]: Define allowed headers for CORS requests
        allow_headers=settings.CORS.ALLOW_HEADERS,
    )
