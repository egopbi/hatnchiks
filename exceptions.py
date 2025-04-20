class CardNotFound(Exception): 
    def __init__(self, game_id: str, card_name: str):
        message = f"Card {card_name} in the game {game_id} wasn't found"
        super().__init__(message)


class NoCardsInTheGame(Exception): 
    def __init__(self, game_id: str, card_name_pattern: str):
        message = f"No cards with pattern {card_name_pattern} in the game {game_id}"
        super().__init__(message)


class ParamNotFound(Exception): 
    def __init__(self, game_id: str, param_name: str):
        message = f"Parameter {param_name} in the game {game_id} wasn't set"
        super().__init__(message)


class HatEmpty(Exception):
    def __init__(self, game_id: str):
        message = f"Hat in the game {game_id} is empty"
        super().__init__(message)


class HatDoesNotExist(Exception):
    def __init__(self, game_id: str):
        message = (
            f"The Hat in the game {game_id} doesn't exist. "
            f"First you need to create it"
        )
        super().__init__(message)


class LastRoundWasEnd(Exception):
    def __init__(self, game_id: str):
        message = f"Last round in the game {game_id} was end"
        super().__init__(message)


class NeedToReloadInfo(Exception):
    def __init__(self, game_id: str):
        message = f"Game {game_id} need to reload info"
        super().__init__(message)


__all__ = [
    "CardNotFound",
    "NoCardsInTheGame",
    "ParamNotFound",
    "HatEmpty",
    "HatDoesNotExist",
    "LastRoundWasEnd",
    "NeedToReloadInfo",
]