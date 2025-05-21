from datetime import datetime, timedelta, timezone
import jwt

from config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.jwt.private_key_path.read_text(),
    algorithm: str = settings.jwt.algorithm,
    expire_minutes: int = settings.jwt.access_token_exp_min,
):
    now = datetime.now(tz=timezone.utc)
    expire = now + timedelta(minutes=expire_minutes)
    
    to_encode = payload.copy()
    to_encode.update(
        exp=expire,
        iat=now
    )
    encoded = jwt.encode(
        payload=to_encode, 
        key=private_key, 
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.jwt.public_key_path.read_text(),
    algorithm: str = settings.jwt.algorithm,
):
    decoded = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm],
    )
    return decoded

# БУДУ ДЕЛАТЬ В КУКИ