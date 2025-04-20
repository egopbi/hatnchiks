from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic_schema import CardSchema

if TYPE_CHECKING:
    from backend_models import HatService


class HatDbRepository(ABC):
    @abstractmethod
    async def put_in_hat(self, card_names: list[str]):
        pass

    @abstractmethod
    async def pop_card(self) -> str | None:
        pass

    @abstractmethod
    async def push_card_to_second_hat(self, card_name: str):
        pass

    @abstractmethod
    async def get_cards_from_second_hat(self) -> list[str]:
        pass
    
    @abstractmethod
    async def clear_second_hat(self):
        pass

    @abstractmethod
    async def get_card_text(self, card_name: str):
        pass


class GameDbRepository(ABC):
    @abstractmethod
    async def add_game_to_active(self):
        pass

    async def add_game(self):
        pass

    @abstractmethod
    async def get_all_card_names(self) -> list[str]:
        pass

    @abstractmethod
    async def get_hat(self) -> "HatService":
        pass

    @abstractmethod
    async def get_card(self, card_id: str) -> str:
        pass

    @abstractmethod
    async def add_card(self, card: CardSchema):
        pass
    
    @abstractmethod
    async def get_round(self) -> int:
        pass

    @abstractmethod
    async def set_round(self, round_num: int):
        pass

    @abstractmethod
    async def get_timer(self) -> int:
        pass

    @abstractmethod
    async def set_timer(self, timer: int):
        pass
    
    @abstractmethod
    async def get_teams_number(self) -> int:
        pass

    @abstractmethod
    async def set_teams_number(self, teams_number: int):
        pass
    
    @abstractmethod
    async def delete_game_info(self):
        pass
