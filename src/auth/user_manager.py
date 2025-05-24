import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from src.models import User
from config import settings
from src.utils.logger import backend_logger


class UserManager(IntegerIDMixin , BaseUserManager[User, int]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret 

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        backend_logger.warning(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        backend_logger.warning(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        backend_logger.warning(f"Verification requested for user {user.id}. Verification token: {token}")
# Говорят, что в логгере не могут быть f-строки. Почему?