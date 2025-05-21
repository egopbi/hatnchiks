
from typing import TYPE_CHECKING
from functools import wraps

from src.exceptions import NeedToReloadInfo, ParamNotFound
from src.utils.logger import database_logger

if TYPE_CHECKING:
    from src.backend.game_services import GameService

def reloader(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        game: GameService = kwargs.get('game')
        if game is None:
            raise ValueError("`game` is required for reloader")

        try:
            res = await func(*args, **kwargs)
            return res
        except NeedToReloadInfo:
            await game.reload_info()
            res = await func(*args, **kwargs)
    return wrapper


def check_for_game_start(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        game: GameService = kwargs.get('game')
        if game is None:
            raise ValueError("`game` is required for reloader")

        try:
            res = await func(*args, **kwargs)
            return res
        except ParamNotFound:
            return {"success": False, "message": "The game has not been started, start it!"}
    return wrapper


def db_try_except(*exceptions):
    def outer(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                res = await func(*args, **kwargs)
                return res
            except exceptions as e:
                database_logger.error(f"Error while runninng {func.__name__}: {str(e)}")
                return False
        return wrapper
    return outer


__all__ = [
    "reloader",
    "check_for_game_start",
    "db_try_except",
]