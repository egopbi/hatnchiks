from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from src.api import main_router
from src.backend.database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.create_tables()  # выполняется один раз при старте
    # можно подключать ещё и Redis, логгеры и т.д.
    yield
    # здесь можно делать graceful shutdown, если нужно


app = FastAPI(lifespan=lifespan)
app.include_router(main_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)