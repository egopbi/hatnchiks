from fastapi import Depends, Form, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jwt import InvalidTokenError

from src import auth
from src.backend.database import DatabaseService, db
from src.exceptions import InvalidTokenException, UnauthorizedUser
from src.auth import validate_password
from src.models.general import User
from src.schemas.game_schemas import UserSchema
from src.utils.logger import backend_logger


#НУЖНО ЛИ МНЕ ИСПОЛЬЗОВАТЬ OAUTH2PASSWORDBEARER, ЕСЛИ Я ХОЧУ РАБОТАТЬ С КУКИ?
def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends("ОТКУДА ПОЛУЧАЕМ ТОКЕН ИЗ КУКИ"),
) -> UserSchema:
    token = credentials.credentials
    try:
        payload = auth.decode_jwt(token=token)
    except InvalidTokenError as e:
        raise InvalidTokenException(e)
    
    return payload


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
) -> UserSchema:
    username:str | None = payload.get("sub")
    if not (user := await db.get_user(username=username)):
        backend_logger.error(f"User {username} is not in the Database")
        raise UnauthorizedUser(user)
    
    return user