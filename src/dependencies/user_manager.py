from fastapi import Depends
from src.auth.user_manager import UserManager
from .database import get_users_db


async def get_user_manager(user_db=Depends(get_users_db)):
    yield UserManager(user_db)