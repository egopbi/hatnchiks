import uuid

from pydantic import BaseModel, Field, ConfigDict


class CardCreateGameSchema(BaseModel):
    user_id: str
    text: str = Field(
        max_length=30, 
        description="Enter character name"
    )
    model_config = ConfigDict(extra='forbid')


class CardSchema(CardCreateGameSchema):
    game_id: str
    card_id: str | None = Field(default=None, init=False)

    def model_post_init(self, __context):
        self.card_id = "card-" + str(uuid.uuid4())[:10]


class GameCreateSchema(BaseModel):
    teams_number: int = Field(
        ge=2, 
        le=10, 
        description="Enter the number of teams (from 2 to 10)"
    )
    timer: int = Field(
        default=60, 
        ge=30, 
        le=120, 
        description="Enter the duration of move in seconds (from 30 to 120)"
    )
    model_config = ConfigDict(extra='forbid')


class UserSchema(BaseModel):
    username: str = Field(min_length=4, max_length=20)
    password: str = Field(min_length=8, max_length=20)
    

__all__ = [
    "CardCreateGameSchema",
    "CardSchema",
    "GameCreateSchema",
]