import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.exception_handlers import http_exception_handler

from storeapi.database import database, create_tables_async
#from storeapi.logging_conf import configure_logging
from storeapi.routers.post import router as post_router
from storeapi.routers.video import router as upload_router
from storeapi.routers.ranking import router as ranking_router
from storeapi.routers.user import router as user_router
from storeapi.routers.vote import router as vote_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    #configure_logging()
    await database.connect()
    await create_tables_async()  # Crear tablas al iniciar la aplicación
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
#app.add_middleware(CorrelationIdMiddleware)
app.include_router(post_router)
app.include_router(upload_router)
app.include_router(user_router)
app.include_router(ranking_router)
app.include_router(vote_router)
