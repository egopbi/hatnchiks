from typing import TYPE_CHECKING

from redis.asyncio import Redis

from config import settings
from src.backend.abstractclasses import HatDbRepository, GameDbRepository
from src.exceptions import *
from src.schemas.game_schemas import CardSchema
if TYPE_CHECKING:
    from src.backend.game_services import HatService


rd = Redis(
    host=settings.rd.host, 
    port=settings.rd.port, 
    db=settings.rd.db, 
    decode_responses=True
)


class HatRedisRepository(HatDbRepository):
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.rd = rd
        self.hat_name = f"{self.game_id}:hat"
        self.second_hat_name = f"{self.game_id}:second_hat"
    
    async def put_in_hat(self, card_names: list[str]):
        await self.rd.rpush(self.hat_name, *card_names)
        return True

    async def pop_card(self) -> str | None:
        res = await self.rd.rpop(self.hat_name)
        if res is None:
            raise HatEmpty(self.game_id)
        return res

    async def push_card_to_second_hat(self, card_name: str):
        await rd.rpush(self.second_hat_name, card_name)
        return True

    async def get_cards_from_second_hat(self) -> list[str]:
        return await self.rd.lrange(name=self.second_hat_name, start=0, end=-1)
    
    async def clear_second_hat(self):
        await self.rd.delete(self.second_hat_name)
        return True

    async def get_card_text(self, card_name: str):
        res = await self.rd.get(name=card_name)
        if res is None:
            raise CardNotFound(self.game_id, card_name)
        return res


class GameRedisRepository(GameDbRepository):
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.rd = rd
        self.card_pattern = f"{self.game_id}:card*"

    async def add_game_to_active(self):
        await self.rd.sadd("active_games", self.game_id)
        return True
    
    async def add_game(self):
        await self.rd.sadd("all_games", self.game_id)
        return True
    
    async def get_all_card_names(self) -> list[str]:
        res = [key async for key in self.rd.scan_iter(match=self.card_pattern)]
        if not res:
            raise NoCardsInTheGame(self.game_id, self.card_pattern)
        return res

    async def get_hat(self) -> "HatService":
        res = await self.rd.lrange(name=f"{self.game_id}:hat", start=0, end=-1)
        return res

    async def get_card(self, card_id: str) -> str:
        card_name = f"{self.game_id}:" + card_id
        res = await self.rd.get(name=card_name)
        if res is None:
            raise CardNotFound(self.game_id, card_name)
        return res
    
    async def add_card(self, card: CardSchema):
        await self.rd.set(name=f"{self.game_id}:{card.card_id}", value=card.text)
        return True
    
    async def get_round(self) -> int:
        res = await self._get_param("round") 
        return int(res)

    async def set_round(self, round_num: int):
        await self.rd.set(name=self._param_to_name("round"), value=round_num)
        return True

    async def get_timer(self) -> int:
        res = await self._get_param("timer")
        return int(res)

    async def set_timer(self, timer: int):
        await self.rd.set(name=self._param_to_name("timer"), value=timer)
        return True
    
    async def get_teams_number(self) -> int:
        res = await self._get_param("teams_number")
        return int(res)

    async def set_teams_number(self, teams_number: int):
        await self.rd.set(name=self._param_to_name("teams_number"), value=teams_number)
        return True
    
    async def delete_game_info(self):
        game_keys = [key async for key in self.rd.scan_iter(match=self.game_id + "*")]
        await self.rd.delete(*game_keys)
        await self.rd.srem("active_games", self.game_id)
        return True

    def _param_to_name(self, obj_name: str) -> str:
        return f"{self.game_id}:" + obj_name
    
    async def _get_param(self, name: str):
        param_name = self._param_to_name(name)
        res = await self.rd.get(name=param_name)
        if res is None:
            raise ParamNotFound(self.game_id, param_name)
        return res


class ProjectRepository:
    def __init__(self):
        self.rd = rd

    async def get_active_games(self):
        res = await rd.smembers("active_games")
        return res

    async def get_all_games(self):
        res = await rd.smembers("all_games")
        return res
