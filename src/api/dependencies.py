from fastapi import Depends, Form, HTTPException, status

from src.backend.database import DatabaseService, db
from src.exceptions import UnauthorizedUser
from src.auth import validate_password
from src.models.general import User
from src.schemas.game_schemas import UserSchema
from src.utils.logger import backend_logger

def get_db() -> DatabaseService:
    return db


async def register_user(user: UserSchema, db: DatabaseService = Depends(get_db)) -> User:
    if await db.get_user(user.username):
        raise HTTPException(status_code=404, detail=f"User {user.username} is already registered")
    
    if not (user_db := await db.create_user(user)):
        raise HTTPException(status_code=404, detail=f"Troubles with db")
    
    return user_db


async def validate_auth_user(
    username: str = Form(),
    password: str = Form(), 
) -> User:
    
    if not (user := await db.get_user(username=username)):
        backend_logger.error(f"User {username} is not in the Database")
        raise UnauthorizedUser(user)
    
    if validate_password(
        password=password,
        hashed_password=user.password,
    ):
        return user
    
    backend_logger.error(f"User's {user} entered an incorrect password")
    raise UnauthorizedUser(user)