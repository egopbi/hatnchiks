import random
import uuid

from config import rd
from src.backend.abstractclasses import GameDbRepository, HatDbRepository
from src.backend.redis import GameRedisRepository, HatRedisRepository
from src.exceptions import CardNotFound, HatEmpty, LastRoundWasEnd, NeedToReloadInfo

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
        self.game_db: GameRedisRepository = game_db
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


# ДАЛЬШЕ ДОБАВЛЕНИЕ ЮЗЕРОВ, АВТОРИЗАЦИЯ, ХРАНЕНИЕ ЮЗЕРОВ В ОТДЕЛЬНОМ СПИСКЕ В РЕДИСЕ