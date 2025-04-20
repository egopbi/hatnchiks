import asyncio
import random
import uuid

from redis.asyncio import Redis

from abstractclasses import HatDbRepository, GameDbRepository
from exceptions import *
from pydantic_schema import CardSchema

rd_host = "localhost"
rd_port = 6379
rd_db = 1

rd = Redis(host=rd_host, port=rd_port, db=rd_db, decode_responses=True)


class HatRedisRepository(HatDbRepository):
    def __init__(self, game_id: str, rd: Redis):
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


class HatService:
    def __init__(self, hat_redis: HatDbRepository, cards_bag: list[str]):
        self.hat_db = hat_redis
        self._cards_bag = cards_bag
        self._game_cards_count = len(cards_bag)
        self.round_count = self._game_cards_count

    @classmethod
    def create_redis(cls, game_id: str, cards_bag: list[str]):
        return cls(hat_redis=HatRedisRepository(game_id=game_id, rd=rd), cards_bag=cards_bag)

    @classmethod
    def create_postgres(cls, game_id: str, cards_bag):
        raise NotImplementedError("Postgres backend is not implemented yet.")

    async def _fill_hat(self, card_names):
        random.shuffle(card_names)
        res = await self.hat_db.put_in_hat(card_names)
        return res
    
    async def first_fill_hat(self):
        return await self._fill_hat(card_names=self._cards_bag)

    async def pull_card(self):
        # if last_card:
        #     return False
        
        try:
            card_name = await self.hat_db.pop_card()
            await self.hat_db.push_card_to_second_hat(card_name=card_name)
            card = await self.hat_db.get_card_text(card_name=card_name)
            self.round_count -= 1
            # if self.round_count < 1:
            #     last_card = True
            return card
        
        except (HatEmpty, CardNotFound):
            # logger.debug(f"Handled known error: {e}")
            raise

    async def next_round(self):
        card_names = await self.hat_db.get_cards_from_second_hat()
        await self._fill_hat(card_names=card_names)
        await self.hat_db.clear_second_hat()
        self.round_count = self._game_cards_count
        return True


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

    async def get_hat(self) -> HatService:
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


class GameService:
    def __init__(
            self,
            game_db: GameDbRepository,
            room_id: str | None, 
            game_id: str,
            cards_per_user: int,
            teams_number: int | None,
            timer: int,
        ):
        self.game_id = game_id
        self.room_id = room_id
        self.teams_number = teams_number
        self.users = ...
        self.timer = timer
        self.cards_per_user = cards_per_user
        self.game_db = game_db
        self.hat = None
        self.round = None
    
    @classmethod
    def create_redis(
        cls,
        game_id: str | None = None,
        room_id: str | None = None, 
        cards_per_user: int = 6,
        teams_number: int | None = None,
        timer: int = 60,
    ):
        game_id = ("game-" + str(uuid.uuid4())[:10] if game_id is None else game_id)
        return cls(
            game_db=GameRedisRepository(game_id=game_id),
            room_id=room_id, 
            game_id=game_id,
            cards_per_user=cards_per_user,
            teams_number=teams_number,
            timer=timer,
        )
    
    async def apply_settings_to_db(self):
        await self.game_db.add_game()
        await self.game_db.set_timer(timer=self.timer)
        await self.game_db.set_teams_number(teams_number=self.teams_number)
        
    async def load_settings_from_db(self):
        self.round = await self.game_db.get_round()
        self.timer = await self.game_db.get_timer()
        self.teams_number = await self.game_db.get_teams_number()
    
    async def create_hat(self):
        cards_bag = await self.game_db.get_all_card_names()
        self.hat = HatService.create_redis(game_id=self.game_id, cards_bag=cards_bag)
    
    async def game_start(self):
        await self.create_hat()
        await self.game_db.add_game_to_active()
        await self.hat.first_fill_hat()
        await self.game_db.set_round(round_num=1)
        self.round = 1
    
    async def next_round(self):
        try:
            self.round += 1
            if self.round > 3:
                raise LastRoundWasEnd(self.game_id)
            
            await self.game_db.set_round(round_num=self.round)
            await self.hat.next_round()
        except TypeError as e:
            # logger.debug(f"self.round is not defined: {e}")
            raise NeedToReloadInfo(self.game_id)

        # Нужен какой-то флаг извне для окончания раунда

    async def pull_card_from_hat(self):
        try:
            card = await self.hat.pull_card()
            return card
        except AttributeError as e:
            # logger.debug(f"self.hat is not defined: {e}")
            raise NeedToReloadInfo(self.game_id)

    async def delete_game(self):
        await self.game_db.delete_game_info()

    async def reload_info(self):
        await self.load_settings_from_db()
        await self.create_hat()


class ProjectInterface:
    def __init__(self):
        self.rd = rd

    async def get_active_games(self):
        res = await rd.smembers("active_games")
        return res

    async def get_all_games(self):
        res = await rd.smembers("all_games")
        return res

"""
async def main():
    game1 = GameInterface(game_id="game-e12f1386-6")
    # cards = []
    # cards.append(CardSchema(game_id=game1.game_id, user_id="eeegorka", text="Tomas Shelby"))
    # cards.append(CardSchema(game_id=game1.game_id, user_id="eeegorka", text="Cesar"))
    # cards.append(CardSchema(game_id=game1.game_id, user_id="eeegorka", text="V Putin"))
    # cards.append(CardSchema(game_id=game1.game_id, user_id="eeegorka", text="Cesar"))
    # cards.append(CardSchema(game_id=game1.game_id, user_id="eeegorka", text="Olya"))

    # tasks = [asyncio.create_task(game1.add_card(card=card)) for card in cards]
    # await asyncio.gather(*tasks)

    await game1.game_start()
    card1 = await game1.pull_card_from_hat()
    print(card1)
    card2 = await game1.pull_card_from_hat()
    print(card2)
    card3 = await game1.pull_card_from_hat()
    print(card3)
    card4 = await game1.pull_card_from_hat()
    print(card4)



if __name__ == "__main__":
    asyncio.run(main())
"""