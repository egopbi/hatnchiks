from functools import lru_cache

from fastapi import Depends

from src.backend.game_services import GameService
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