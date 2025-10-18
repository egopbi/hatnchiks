import asyncio
import contextlib
import sys

from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))


from src.auth import UserManager
from src.dependencies import get_users_db, get_user_manager
from src.models import User
from src.schemas.users import UserCreate
from src.backend.database import db
# from fastapi_users.exceptions import UserAlreadyExists

# get_async_session
# get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_users_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

default_email = "admin@admin.com"
default_password = "abc"
default_nickname = "admin"
default_is_active = True
default_is_superuser = True
default_is_verified = True

async def create_user(
        user_manager: UserManager,
        user_create: UserCreate,
):
    user: User  = await user_manager.create(
        user_create=user_create,
        safe=False,
    )
    return user


async def create_superuser(
        email: str = default_email,
        password: str = default_password,
        nickname: str = default_nickname,
        is_active: bool = default_is_active,
        is_superuser: bool = default_is_superuser,
        is_verified: bool = default_is_verified,

):
    user_create = UserCreate(
        email=email,
        password=password,
        nickname=nickname,
        is_active=is_active,
        is_superuser=is_superuser,
        is_verified=is_verified,
    )

    async with db.db_conn.async_session() as session:
        async with get_user_db_context(session) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                return await create_user(
                    user_manager=user_manager,
                    user_create=user_create ,
                )


# Тут ошибка с асихнорнным контекстным менеджером
if __name__ == "__main__":
    asyncio.run(create_superuser())