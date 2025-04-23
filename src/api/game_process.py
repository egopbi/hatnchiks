from fastapi import APIRouter, Depends

from src.api.helpers import check_for_game_start, get_game, reloader
from src.backend.game_services import GameService
from src.exceptions import HatEmpty, LastRoundWasEnd


router = APIRouter(tags=["Game Process"])


@router.post("/games/{game_id}/pull_card")
@check_for_game_start
@reloader
async def pull_card_from_hat(game: GameService = Depends(get_game)):
    try:
        card = await game.pull_card_from_hat()
        return {"success": True, "message": f"Text on card '{card}'"}
    except HatEmpty:
        return {"success": False, "message": f"The hat is empty. Start next round!"}
    # Вылетает пятисотка, если не стартуешь игру


@router.post("/games/{game_id}/next_round")
@check_for_game_start
@reloader
async def go_to_next_round(game: GameService = Depends(get_game)):
    try:
        await game.next_round()
        return {"success": True, "message": f"The game moves to the next round"}
    except LastRoundWasEnd:
        return {"success": False, "message": f"The game was end!"}
    