from typing import TYPE_CHECKING

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from src.backend.database import DatabaseService, db
from src.models import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def get_db() -> DatabaseService:
    return db


def get_users_db(session: "AsyncSession" = Depends(db.db_conn.get_async_session)):
    yield User.get_db(session=session)
