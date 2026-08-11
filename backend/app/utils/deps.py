"""Shared FastAPI dependencies — primarily auth guards for protected routes."""
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.database import get_users_collection
from app.models.user import UserModel
from app.utils.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> UserModel:
    """Resolve the JWT bearer token to the requesting user, or raise 401."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        user_id = decode_access_token(credentials.credentials)
        object_id = ObjectId(user_id)
    except (JWTError, InvalidId):
        raise unauthorized

    users = get_users_collection()
    user_doc = await users.find_one({"_id": object_id})
    if user_doc is None:
        raise unauthorized

    return UserModel(**user_doc)
