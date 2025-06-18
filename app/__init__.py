from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from controllers.Media import MEDIA_DIR
from .db import create_db_and_tables
from views import routers

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run at startup
    create_db_and_tables()
    yield
    # Code to run at shutdown

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    # Register routers
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
    for router in routers:
        app.include_router(router)
    return app
