from fastapi import APIRouter, Depends, HTTPException

from src import auth
from src.api.dependencies import get_db, validate_auth_user, register_user
from src.api.helpers import get_game
from src.backend.database import DatabaseService
from src.models.general import User
from src.schemas.game_schemas import TokenInfo, UserSchema

router = APIRouter(tags=["Users"])


@router.post("/users/register")
async def register_new_user(user_db: User = Depends(register_user)):
    return {"success": True, "message": f"User {user_db.username} has been added"}


@router.get("/users/register")
async def get_user(username: str, db: DatabaseService = Depends(get_db)):
    user = await db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{username}' isn't in the Database")
    
    return {"success": True, "message": f"User '{username}' already in the Database"}


@router.post("/users/login")
async def auth_user_jwt(
    user: UserSchema = Depends(validate_auth_user),
):
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
    }
    token =  auth.encode_jwt(payload=jwt_payload)
    return TokenInfo(
        access_token=token,
        token_type="Bearer",
    )


    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )



