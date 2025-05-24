from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

from config import settings


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.jwt.private_key_path.read_text(),
        lifetime_seconds=settings.jwt.access_token_lifetime_seconds,
        algorithm=settings.jwt.algorithm,
        public_key=settings.jwt.public_key_path.read_text(),
        )

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)