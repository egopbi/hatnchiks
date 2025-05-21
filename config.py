from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

BASE_DIR = Path(__file__).parent
SENSITIVE_DIR = BASE_DIR / "sensitive"


class DbSettings(BaseSettings):
    url: str 
    echo: bool


class RdSettings(BaseSettings):
    host: str
    port: str
    db: str


class AuthJWT(BaseSettings):
    private_key_path: Path =  SENSITIVE_DIR / "jwt" / "jwt_private.pem"
    public_key_path: Path = SENSITIVE_DIR / "jwt" / "jwt_public.pem"
    algorithm: str = "RS256"
    access_token_exp_min: int = 15


class Settings(BaseSettings):
    db: DbSettings
    rd: RdSettings
    jwt: AuthJWT = Field(default_factory=AuthJWT)

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__" )


settings = Settings()
