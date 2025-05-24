from typing import TYPE_CHECKING
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.orm import Mapped, mapped_column

from .general import str20, Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class User(Base, SQLAlchemyBaseUserTable[int]):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str20] = mapped_column(primary_key=True)
    password: Mapped[bytes]
    
    @classmethod
    def get_db(cls, session:"AsyncSession"):
        return SQLAlchemyUserDatabase(
            session=session, 
            user_table=User
        )