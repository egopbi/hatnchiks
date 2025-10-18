import json
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from main import app


@pytest_asyncio.fixture(scope="class")
async def async_client_context(request):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test/api",
    ) as ac:
        request.cls.ac = ac
        yield 


async def create_test_game(client):
    res = await client.post(
        "/games", 
        params={"teams_number": 4, "timer": 45},
    )
    assert res.status_code == 200
    data = json.loads(res.text)
    assert data.get("success") == True
    return data.get("game_id")
    


@pytest.mark.usefixtures("async_client_context")
class TestAPIGames:
    @pytest.mark.asyncio
    async def test_get_all_games(self):
        raw_res = await self.ac.get("/games")
        assert raw_res.status_code == 200
        print(raw_res.text, "\n\n\n")
        res = json.loads(raw_res.text)
        assert res.get("success") == True

    @pytest.mark.asyncio
    async def test_post_create_game(self):
        game_id = await create_test_game(self.ac)
        assert isinstance(game_id, str)
    
    @pytest.mark.asyncio
    async def test_get_active_games(self):
        raw_res = await self.ac.get("/games/active")
        assert raw_res.status_code == 200
        res = json.loads(raw_res.text)
        print(res, "\n\n\n")
        assert res.get("success") == True
    
    @pytest.mark.asyncio
    async def test_add_player_to_game(self):
        game_id = await create_test_game(self.ac)
        raw_res = await self.ac.post(f"/games/{game_id}/")
        assert raw_res.status_code == 200
        print(raw_res.text, "\n\n\n")
        res = json.loads(raw_res.text)
        assert res.get("success") == True
        
 
 # В чатгпт в pytest рекомендации по изменению redis

"""

@router.post("/games/{game_id}/players")
async def add_player_to_game(
    game: GameService = Depends(get_game),
    user: User = Depends(current_user),

):
    res = await game.add_user(user)    
    return {"success": True, "message": f"Player add: {res}"}


@router.get("/games/{game_id}/players")
@check_user_in_game
async def get_game_players(
    game: GameService = Depends(get_game),
    user: User = Depends(current_user),

):
    users = await game.get_games_users()    
    return {"success": True, "message": f"Players: {users}"}


@router.post("/games/{game_id}/start")
async def start_game(game: GameService = Depends(get_game)):
    await game.game_start()
    return {"success": True, "message": f"Game '{game.game_id}' was started"}


@router.get("/games/{game_id}")
async def get_game_info(game: GameService = Depends(get_game)):
    if game.teams_number is None:
        await game.reload_info() #Мб эту проверку перенести в декоратор

    info = await game.game_info()
    return {"success": True, "message": info}


@router.delete("/games/{game_id}")
async def delete_game(game: GameService = Depends(get_game)):
    game_id = game.game_id
    await game.delete_game() 
    return {"success": True, "message": f"The game {game_id} was deleted"}


@router.post("/games/{game_id}")
async def end_game(game: GameService = Depends(get_game)):
    await game.delete_game() 
    # Переносить данные игры в базу данных
    return {"success": True, "message": f"The game was deleted"}
        """