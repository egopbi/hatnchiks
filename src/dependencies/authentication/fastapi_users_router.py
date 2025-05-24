from fastapi_users import FastAPIUsers

from .user_manager import get_user_manager
from src.auth import auth_backend
from src.models import User


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)