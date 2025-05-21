from fastapi import APIRouter, Depends

from src.api.helpers import create_game_service, get_game
from src.backend.game_services import GameService
from src.backend.redis import ProjectRepository


router = APIRouter(tags=["Games"])
proj = ProjectRepository()
# НАДО КУДА-ТО ПЕРЕНЕСТИ

@router.get("/games")
async def get_all_games():
    res = await proj.get_all_games()
    if len(res) == 0:
        return {"success": False, "message": f"There is no active games"}
    
    return {"success": True, "message": f"All games: {res}"}


@router.get("/games/active")
async def get_active_games():
    res = await proj.get_active_games()
    if len(res) == 0:
        return {"success": False, "message": f"There is no active games"}
    
    return {"success": True, "message": f"Active games: {res}"}


@router.post("/games")
async def create_game(game: GameService = Depends(create_game_service)):
    # Сюда нужно передавать параметры игры
    await game.apply_settings_to_db()
    return {"success": True, "message": f"Game '{game.game_id}' was created"}


@router.post("/games/{game_id}")
async def start_game(game: GameService = Depends(get_game)):
    await game.game_start()
    return {"success": True, "message": f"Game '{game.game_id}' was started"}


@router.delete("/games/{game_id}")
async def delete_game(game: GameService = Depends(get_game)):
    await game.delete_game() 
    return {"success": True, "message": f"The game was deleted"}


@router.post("/games/{game_id}")
async def end_game(game: GameService = Depends(get_game)):
    await game.delete_game() 
    # Переносить данные игры в базу данных
    return {"success": True, "message": f"The game was deleted"}
        