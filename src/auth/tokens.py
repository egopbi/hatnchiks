from datetime import datetime, timedelta, timezone
import jwt

from config import settings

#НЕНУЖНЫЙ РАЗДЕЛ, ТАК КАК ЕСТЬ AUTH.BACKEND

def encode_jwt(
    payload: dict,
    private_key: str = settings.jwt.private_key_path.read_text(),
    algorithm: str = settings.jwt.algorithm,
    expire_seconds: int = settings.jwt.access_token_lifetime_seconds,
):
    now = datetime.now(tz=timezone.utc)
    expire = now + timedelta(seconds=expire_seconds)
    
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
