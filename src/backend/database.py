import asyncio
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy.sql import func

from config import settings
from src.auth.password_check import hash_password
from src.models.general import Base, User
from src.schemas.game_schemas import UserSchema
from src.utils.decorators import db_try_except
from src.utils import database_logger


class DatabaseService():
    def __init__(self):
        self.engine = create_async_engine(url=settings.db.url, echo=settings.db.echo, future=True)

        self.async_session = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    @db_try_except(Exception)
    async def create_tables(self) -> bool:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            database_logger.success("All metadata was created")
            return True

    @db_try_except(Exception)        
    async def create_user(self, user_form: UserSchema) -> User:
        async with self.async_session() as session:
            hashed_pw = hash_password(user_form.password)
            user_db = User(username=user_form.username, password=hashed_pw)
            session.add(user_db)
            await session.commit()
            database_logger.success(f"User {user_db} has been added")
            return user_db
           
    @db_try_except(Exception)        
    async def get_user(self, username: str):
        async with self.async_session() as session:
            res = await session.execute(
                select(User)
                .filter(User.username == username)
            )
            ans: User = res.scalars().one()
            
            database_logger.success(f"User {username} has been found")
            return ans
           

db = DatabaseService()