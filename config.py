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
    naming_conventions: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s" ,
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }


class RdSettings(BaseSettings):
    host: str
    port: str
    db: str


class AuthJWT(BaseSettings):
    private_key_path: Path =  SENSITIVE_DIR / "jwt" / "jwt_private.pem"
    public_key_path: Path = SENSITIVE_DIR / "jwt" / "jwt_public.pem"
    algorithm: str = "RS256"
    access_token_lifetime_seconds: int = 3600


class AccessToken(BaseSettings):
    reset_password_token_secret: str
    verification_token_secret: str


class Settings(BaseSettings):
    db: DbSettings
    rd: RdSettings
    access_token: AccessToken
    jwt: AuthJWT = Field(default_factory=AuthJWT)

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__" )


settings = Settings()
