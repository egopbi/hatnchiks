from fastapi import APIRouter

from src.api.cards import router as cards_router
from src.api.game_process import router as game_process_router
from src.api.games import router as games_router


main_router = APIRouter()
main_router.include_router(cards_router)
main_router.include_router(game_process_router)
main_router.include_router(games_router)