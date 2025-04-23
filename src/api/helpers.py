from functools import lru_cache, wraps

from fastapi import Depends

from src.backend.game_services import GameService
from src.exceptions import NeedToReloadInfo, ParamNotFound
from src.schemas.game_schemas import GameCreateSchema


@lru_cache(maxsize=100)
def get_game(
    game_id: str, 
) -> GameService:
    return GameService.create_redis(game_id=game_id)


def create_game_service(game: GameCreateSchema = Depends()) -> GameService:
    return GameService.create_redis(
        teams_number=game.teams_number,
        timer=game.timer,
    )


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