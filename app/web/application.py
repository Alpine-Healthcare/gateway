from importlib import metadata
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import UJSONResponse

from fastapi.staticfiles import StaticFiles

from logging.config import dictConfig
import logging
from app.utils.log_config import LogConfig

dictConfig(LogConfig().dict())
logger = logging.getLogger("mycoolapp")

from app.services.pdfs.ipfs import start_ipfs
from app.web.api.router import api_router
from app.web.gql.router import gql_router
from app.web.lifetime import register_shutdown_event, register_startup_event

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="PDOS Gateway",
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

    start_ipfs()

    return app
