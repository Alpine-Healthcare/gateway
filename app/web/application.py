from importlib import metadata
from pathlib import Path
import logging
from logging.config import dictConfig

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.utils.log_config import LogConfig

dictConfig(LogConfig().dict())
logger = logging.getLogger("Gateway")

from app.web.api.router import api_router
from app.web.lifetime import register_shutdown_event, register_startup_event

# Define the allowed origins
origins = [
    "http://localhost:3000",  # Frontend development server
]

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="Gateway",
        version=metadata.version("app"),
        docs_url=None,
        redoc_url=None,
        openapi_url="/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)

    # Main router for the API.
    app.include_router(router=api_router)
    # Graphql router
    #app.include_router(router=gql_router, prefix="/graphql")
    # Adds static directory.
    # This directory is used to access swagger files.
    app.mount(
        "/public",
        StaticFiles(directory=APP_ROOT / "public"),
        name="public",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # List of allowed origins
        allow_credentials=True,  # Allow cookies or Authorization headers
        allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
        allow_headers=["*"],  # Allow all headers
    )

    return app
