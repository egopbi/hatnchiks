from functools import lru_cache, wraps

from fastapi import FastAPI, HTTPException, Depends
import uvicorn

from exceptions import *
from backend_models import ProjectInterface, GameService
from pydantic_schema import *

app = FastAPI()
proj = ProjectInterface()


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
            return {"success": False, "message": f"The game has not been started, start it!"}
    return wrapper


@app.get("/games", tags=["General"])
async def get_all_games():
    res = await proj.get_all_games()
    if len(res) == 0:
        return {"success": False, "message": f"There is no active games"}
    
    return {"success": True, "message": f"All games: {res}"}


@app.get("/games/active", tags=["General"])
async def get_active_games():
    res = await proj.get_active_games()
    if len(res) == 0:
        return {"success": False, "message": f"There is no active games"}
    
    return {"success": True, "message": f"Active games: {res}"}


@app.post("/games", tags=["Preparation"])
async def create_game(game: GameService = Depends(create_game_service)):
    # Сюда нужно передавать параметры игры
    await game.apply_settings_to_db()
    return {"success": True, "message": f"Game '{game.game_id}' was created"}


@app.get("/games/{game_id}/cards/{card_id}", tags=["General"])
async def get_game_card(card_id: str, game: GameService = Depends(get_game)):
    card = await game.game_db.get_card(card_id=card_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Card '{card_id}' doesn't exist")
    
    return {"success": True, "message": card}


@app.get("/games/{game_id}/cards", tags=["General"])
async def get_all_game_cards(game: GameService = Depends(get_game)):
    cards = await game.game_db.get_all_card_names()
    
    return {"success": True, "message": cards}


@app.post("/games/{game_id}/cards", tags=["General"])
async def add_game_card(
    raw_card: CardCreateGameSchema, 
    game: GameService = Depends(get_game)
):
    
    card = CardSchema(game_id=game.game_id, **raw_card.model_dump())
    await game.game_db.add_card(card=card)
    return {"success": True, "message": f"Card '{card.card_id}' was added"}


@app.post("/games/{game_id}", tags=["Game"])
async def start_game(game: GameService = Depends(get_game)):
    await game.game_start()
    return {"success": True, "message": f"Game '{game.game_id}' was started"}


@app.post("/games/{game_id}/pull_card", tags=["Game"])
@check_for_game_start
@reloader
async def pull_card_from_hat(game: GameService = Depends(get_game)):
    try:
        card = await game.pull_card_from_hat()
        return {"success": True, "message": f"Text on card '{card}'"}
    except HatEmpty:
        return {"success": False, "message": f"The hat is empty. Start next round!"}
    # Вылетает пятисотка, если не стартуешь игру


@app.post("/games/{game_id}/next_round", tags=["Game"])
@check_for_game_start
@reloader
async def go_to_next_round(game: GameService = Depends(get_game)):
    try:
        await game.next_round()
        return {"success": True, "message": f"The game moves to the next round"}
    except LastRoundWasEnd:
        return {"success": False, "message": f"The game was end!"}
    

@app.delete("/games/{game_id}", tags=["General"])
async def delete_game(game: GameService = Depends(get_game)):
    await game.delete_game() 
    return {"success": True, "message": f"The game was deleted"}
        
        
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)