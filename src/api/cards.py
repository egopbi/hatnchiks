from fastapi import APIRouter, Depends, HTTPException

from src.api.helpers import get_game
from src.backend.game_services import GameService
from src.schemas.game_schemas import CardCreateGameSchema, CardSchema

router = APIRouter(tags=["Cards"])


@router.get("/games/{game_id}/cards/{card_id}")
async def get_game_card(card_id: str, game: GameService = Depends(get_game)):
    card = await game.game_db.get_card(card_id=card_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Card '{card_id}' doesn't exist")
    
    return {"success": True, "message": card}


@router.post("/games/{game_id}/cards")
async def add_game_card(
    raw_card: CardCreateGameSchema, 
    game: GameService = Depends(get_game)
):
    
    card = CardSchema(game_id=game.game_id, **raw_card.model_dump())
    await game.game_db.add_card(card=card)
    return {"success": True, "message": f"Card '{card.card_id}' was added"}


@router.get("/games/{game_id}/cards")
async def get_all_game_cards(game: GameService = Depends(get_game)):
    cards = await game.game_db.get_all_card_names()
    
    return {"success": True, "message": cards}


