from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import uvicorn

from src.api import main_router
from src.backend.database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # можно подключать ещё и Redis, логгеры и т.д.
    yield
    # здесь можно делать graceful shutdown, если нужно
    await db.db_conn.dispose()


app = FastAPI(default_response_class=ORJSONResponse, lifespan=lifespan)
app.include_router(main_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)