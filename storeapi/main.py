from contextlib import asynccontextmanager
from fastapi import FastAPI
from storeapi.database import database
from storeapi.routers.post import router as post_router
from storeapi.routers.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(post_router)
app.include_router(user_router)
