from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from controllers.Media import MEDIA_DIR
from .db import create_db_and_tables
from views import routers

origins = [
    "http://www.reservio.space",
    "https://www.reservio.space",
    "http://reservio.space",
    "https://reservio.space"
]



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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
